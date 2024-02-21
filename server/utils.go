package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"net"
	"strings"
	"sync"
	"time"
)

// Shared variable for reconnecting player to respective goroutine
var reconnect = make([]Reconnect, 0)
var mutex sync.Mutex

// Current player id to be assigned
var currentPlayerID int = 0

func writeToClient(conn net.Conn, message string) error {
	_, err := conn.Write([]byte(message + "\n"))

	if err != nil {
		fmt.Println("Error writing: ", err.Error())
		return err
	}

	return nil
}

func writeToPlayer(player *Player, message string) {
	err := writeToClient(player.conn, message)

	if err != nil {
		fmt.Println("Setting player inactive, error : ", err)
		player.active = false
	}
}

func receiveFromClient(conn net.Conn, timeOut time.Duration) (string, error) {

	// Create a buffered reader for the connection
	reader := bufio.NewReader(conn)

	err := conn.SetReadDeadline(time.Now().Add(timeOut * time.Second))

	if err != nil {
		fmt.Println("Error setting read deadline:", err)
		return "", err
	}

	data, err := reader.ReadString(MESS_SEPARATOR)

	if err != nil {
		return "", err
	}

	return data, nil
}

func validateData(data string, isRequest bool, messType string) bool {
	req := strings.Split(data, "=")

	var messageTypeKey = ""

	if isRequest {
		messageTypeKey = "request_type"
	} else {
		messageTypeKey = "response_type"
	}

	if strings.Contains(data, "?") {
		if strings.Compare(req[0], messageTypeKey) != 0 || strings.Compare(strings.Split(req[1], "?")[0], messType) != 0 {
			return false
		}
	} else if strings.Compare(req[0], messageTypeKey) != 0 || strings.Compare(strings.Split(req[1], "\n")[0], messType) != 0 {
		return false
	}

	return true
}

func getConn(listener net.Listener) (net.Conn, bool) {

	// Setting deadline for listening for new connections
	err := listener.(*net.TCPListener).SetDeadline(time.Now().Add(NEW_CONN_WAIT_TIME * time.Second))

	if err != nil {
		fmt.Println("Error setting deadline:", err)
		return nil, false
	}

	// Listen for an incoming connection.
	conn, err := listener.Accept()

	if err != nil {
		return nil, false

	} else if !validateNewConnection(conn) {

		err = writeToClient(conn, "response_type=error&status_code=400\n")

		if err != nil {
			fmt.Println("Error writing: ", err.Error())
		}

		_ = conn.Close()

		return nil, false
	}

	return conn, true
}

// Handles incoming requests.
func validateNewConnection(conn net.Conn) bool {
	// Handshake validation
	mess, err := receiveFromClient(conn, LOBBY_TIME_OUT)

	if err != nil {
		return false
	}

	return validateData(mess, true, "handshake")
}

func removeConn(slice []net.Conn, index int) []net.Conn {
	return append(slice[:index], slice[index+1:]...)
}

func removePlayer(slice []Player, index int) []Player {
	return append(slice[:index], slice[index+1:]...)
}

func getFirstNPlayers(slice []Player, count int) ([]Player, []Player) {
	newSlice := slice
	players := make([]Player, 0)

	for i := 0; i < count; i++ {
		players = append(players, newSlice[0])
		newSlice = removePlayer(newSlice, 0)
	}

	return newSlice, players
}

func removeCard(slice []Card, index int) []Card {
	return append(slice[:index], slice[index+1:]...)
}

func removeFirstNCards(slice []Card, count int) []Card {
	newSlice := slice

	for i := 0; i < count; i++ {
		newSlice = removeCard(newSlice, 0)
	}

	return newSlice
}

func shuffleCards(cards []Card) []Card {
	rand.Shuffle(len(cards), func(i, j int) {
		cards[i], cards[j] = cards[j], cards[i]
	})

	return cards
}

func drawCard(cards []Card) (Card, []Card) {
	return cards[0], removeFirstNCards(cards, 1)
}

func drawNCards(cards []Card, count int) ([]Card, []Card) {
	drawnCards := make([]Card, 0)

	for i := 0; i < count; i++ {
		// Draw card from deck
		drawnCard, newDeck := drawCard(cards)
		cards = newDeck

		drawnCards = append(drawnCards, drawnCard)
	}

	return drawnCards, cards
}

func arePlayersEqual(p1, p2 Player) bool {
	return p1.playerId == p2.playerId
}

func areCardsEqual(c1, c2 Card) bool {
	return c1.cardValue == c2.cardValue && c1.cardType == c2.cardType
}

func doesPlayerHaveCard(player Player, card Card) bool {
	for _, playerCard := range player.cards {
		if areCardsEqual(card, playerCard) {
			return true
		}
	}

	return false
}

func removePlayerCard(player *Player, card Card) {
	var toRemove int

	for index, playerCard := range player.cards {
		if areCardsEqual(card, playerCard) {
			toRemove = index
		}
	}

	player.cards = removeCard(player.cards, toRemove)
	player.cardCount--
}

func canCardBePlayed(card Card, game Game) bool {

	if game.currentCardType == "" {
		if card.cardType == game.topCard.cardType || card.cardValue == game.topCard.cardValue || card.cardValue == "top" {
			return true
		}
	} else {
		if card.cardType == game.currentCardType || card.cardValue == "top" {
			return true
		}
	}

	return false
}

func removeReconnect(slice []Reconnect, index int) []Reconnect {
	return append(slice[:index], slice[index+1:]...)
}

func connectToLobby(player Player, lobby *[]net.Conn) {
	*lobby = append(*lobby, player.conn)
}
