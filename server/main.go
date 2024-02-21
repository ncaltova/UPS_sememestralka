package main

import (
	"errors"
	"fmt"
	"net"
	"os"
	"strconv"
	"strings"
)

func main() {

	// Lobby and wait room init
	var lobbyConns = make([]net.Conn, 0)
	var waitRoomPlayers = make([]Player, 0)
	var ip string
	var port string

	// Listen for incoming connections.
	if len(os.Args[1:]) == 2 {
		if net.ParseIP(os.Args[1]) == nil {
			fmt.Printf("IP Address: %s - Invalid\n", os.Args[1])
			os.Exit(1)
		}

		ip = os.Args[1]

		portNum, err := strconv.Atoi(os.Args[2])

		if err != nil || portNum < 0 || portNum > 65535 {
			fmt.Printf("Port: %s - Invalid\n", os.Args[2])
			os.Exit(1)
		}

		port = os.Args[2]
	} else {
		ip = ""
		port = CONN_PORT
	}

	l, err := net.Listen(CONN_TYPE, ip+":"+port)

	if err != nil {
		fmt.Println("Error listening:", err.Error())
		os.Exit(1)
	}

	fmt.Printf("Server now listening on address %s\n", l.Addr().String())

	// Close the listener when the application closes.
	defer func(l net.Listener) {
		_ = l.Close()
	}(l)

	for {
		checkNewConns(l, &lobbyConns)
		checkLobby(&lobbyConns, &waitRoomPlayers)
		checkWaitRoom(&waitRoomPlayers, &lobbyConns)
	}

}

func checkNewConns(listener net.Listener, lobby *[]net.Conn) {
	conn, valid := getConn(listener)

	if valid {
		err := writeToClient(conn, "response_type=handshake&status_code=200")

		if err != nil {
			_ = conn.Close()
		} else {
			*lobby = append(*lobby, conn)
		}
	}
}

func checkLobby(lobby *[]net.Conn, waitRoom *[]Player) {
	connsToRemove := make([]int, 0)

	for index, element := range *lobby {
		mess, err := receiveFromClient(element, LOBBY_TIME_OUT)

		if err != nil {
			// Check if the error is due to a timeout
			var netErr net.Error
			if !(errors.As(err, &netErr) && netErr.Timeout()) {
				_ = (*lobby)[index].Close()
				connsToRemove = append(connsToRemove, index)
				continue
			}
		}

		if len(mess) == 0 {
			continue
		}

		if validateData(mess, true, "join_game") {
			if strings.Contains(mess, "player_id") {
				reconn := Reconnect{mess, element}

				err = writeToClient(element, "response_type=join_game&status_code=200")

				if err != nil {
					_ = (*lobby)[index].Close()
					connsToRemove = append(connsToRemove, index)
					continue
				}

				mutex.Lock()
				reconnect = append(reconnect, reconn)
				mutex.Unlock()

			} else {
				player := Player{conn: element, playerId: currentPlayerID, active: true}

				err = writeToClient(element, fmt.Sprintf("response_type=join_game&status_code=200&player_id=%d", currentPlayerID))

				if err != nil {
					_ = (*lobby)[index].Close()
					connsToRemove = append(connsToRemove, index)

					// Setup next player id
					currentPlayerID = (currentPlayerID + 1) % 1000

					continue
				}

				*waitRoom = append(*waitRoom, player)

				// Setup next player id
				currentPlayerID = (currentPlayerID + 1) % 1000
			}

			connsToRemove = append(connsToRemove, index)
		} else if validateData(mess, true, "exit") {
			connsToRemove = append(connsToRemove, index)
			_ = writeToClient(element, "response_type=exit&status_code=200")
			_ = element.Close()
		} else if validateData(mess, true, "is_alive") {
			err = writeToClient(element, "response_type=is_alive&status_code=200")

			if err != nil {
				_ = (*lobby)[index].Close()
				connsToRemove = append(connsToRemove, index)
			}
		} else if validateData(mess, true, "game_state") {
			err = writeToClient(element, "response_type=error&status_code=300")

			if err != nil {
				_ = (*lobby)[index].Close()
				connsToRemove = append(connsToRemove, index)
			}
		} else if validateData(mess, true, "player_deck") {
			err = writeToClient(element, "response_type=error&status_code=300")

			if err != nil {
				_ = (*lobby)[index].Close()
				connsToRemove = append(connsToRemove, index)
			}
		} else {
			err = writeToClient(element, "response_type=error&status_code=400")

			if err != nil {
				_ = (*lobby)[index].Close()
				connsToRemove = append(connsToRemove, index)
			}
		}
	}

	for loopIndex, index := range connsToRemove {
		*lobby = removeConn(*lobby, index-loopIndex)
	}
}

func checkWaitRoom(waitRoom *[]Player, lobby *[]net.Conn) {
	var netErr net.Error
	playersToRemove := make([]int, 0)

	for index, player := range *waitRoom {

		data, err := receiveFromClient(player.conn, LOBBY_TIME_OUT)

		if err != nil {
			if !(errors.As(err, &netErr) && netErr.Timeout()) {
				_ = player.conn.Close()
				playersToRemove = append(playersToRemove, index)
				continue
			}
		}

		if len(data) == 0 {
			continue
		}

		if validateData(data, true, "is_alive") {
			err = writeToClient(player.conn, "response_type=is_alive&status_code=200")

			if err != nil {
				_ = player.conn.Close()
				playersToRemove = append(playersToRemove, index)
			}

		} else if validateData(data, true, "leave_game") {
			err = writeToClient(player.conn, "response_type=leave_game&status_code=200")

			if err != nil {
				_ = player.conn.Close()
			} else {
				*lobby = append(*lobby, player.conn)
			}

			playersToRemove = append(playersToRemove, index)
		} else if validateData(data, true, "game_state") {
			err = writeToClient(player.conn, "response_type=error&status_code=300")

			if err != nil {
				_ = player.conn.Close()
				playersToRemove = append(playersToRemove, index)
			}

		} else if validateData(data, true, "player_deck") {
			err = writeToClient(player.conn, "response_type=error&status_code=300")

			if err != nil {
				_ = player.conn.Close()
				playersToRemove = append(playersToRemove, index)
			}
		}
	}

	for loopIndex, index := range playersToRemove {
		*waitRoom = removePlayer(*waitRoom, index-loopIndex)
	}

	if len(*waitRoom) >= 4 {
		wRoom, players := getFirstNPlayers(*waitRoom, 4)
		*waitRoom = wRoom

		go game(players, lobby)
		return

	} else if len(*waitRoom) == 3 {
		wRoom, players := getFirstNPlayers(*waitRoom, 3)
		*waitRoom = wRoom

		go game(players, lobby)
		return
	} else if len(*waitRoom) == 2 {
		wRoom, players := getFirstNPlayers(*waitRoom, 2)
		*waitRoom = wRoom

		go game(players, lobby)
		return
	} else {
		return
	}
}
