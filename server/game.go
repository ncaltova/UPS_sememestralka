package main

import (
	"bytes"
	"errors"
	"fmt"
	"net"
	"strconv"
	"strings"
)

func game(players []Player, lobby *[]net.Conn) {
	// Game init
	deck := shuffleCards(getStartDeck())

	game := Game{players, &players[0], 0, deck[0], make([]Card, 0), deck, ""}
	game.gameDeck = removeFirstNCards(game.gameDeck, 1)
	game.topCard.hasBeenUsed = true

	err, winner := gameService(&game, lobby)

	if err != nil {
		for index, player := range game.players {
			if !player.active {
				_ = player.conn.Close()
			} else {
				connectToLobby(game.players[index], lobby)
			}
		}
		return
	}

	recv := 0
	for recv < len(game.players) {
		for index := range game.players {
			if handleLastRequest(&game.players[index], winner, &game) {
				connectToLobby(game.players[index], lobby)
				recv++
			}
		}
	}

	return
}

func handleLastRequest(player *Player, winner *Player, game *Game) bool {
	if !player.active {
		_ = player.conn.Close()
	}

	data, err := receiveFromClient(player.conn, GAME_TIME_OUT)

	if err != nil {
		// Check if the error is due to a timeout
		var netErr net.Error
		if !(errors.As(err, &netErr) && netErr.Timeout()) {
			player.active = false
			return true
		}
		return false
	}

	if len(data) > 0 {
		if validateData(data, true, "game_end") {
			writeToPlayer(player, fmt.Sprintf("response_type=game_end&status_code=200&winner=%d", winner.playerId))
			return true
		} else if validateData(data, true, "game_state") {
			sendGameState(player, game)
		} else if validateData(data, true, "player_deck") {
			sendPlayerDeck(player)
		} else {
			writeToPlayer(player, "response_type=error&status_code=300")
		}
	}

	return false
}

func sendGameState(player *Player, game *Game) {
	var buffer bytes.Buffer

	for _, p := range game.players {
		if !arePlayersEqual(*player, p) {
			buffer.WriteString(fmt.Sprintf("player_id=%d&count=%d&is_active=%t;", p.playerId, p.cardCount, p.active))
		}
	}

	message := fmt.Sprintf("response_type=game_state&status_code=200&current_player_id=%d&players=[%s]&top_card=[card_type=%s&card_value=%s]&current_type=%s", game.currentPlayer.playerId, buffer.String()[:buffer.Len()-1], game.topCard.cardType, game.topCard.cardValue, game.currentCardType)

	writeToPlayer(player, message)
}

func initPlayerDeck(player *Player, mainDeck *[]Card) {
	playerDeck := make([]Card, 0)

	// Shuffle deck
	shuffleCards(*mainDeck)

	// Get cards for player
	player.cardCount = START_CARD_COUNT

	for i := 0; i < 4; i++ {
		playerDeck = append(playerDeck, (*mainDeck)[i])
	}

	*mainDeck = removeFirstNCards(*mainDeck, 4)
	player.cards = playerDeck
	player.cardCount = 4
}

func sendPlayerDeck(player *Player) {
	var buffer bytes.Buffer

	if len(player.cards) > 0 {
		for _, card := range player.cards {
			buffer.WriteString(fmt.Sprintf("card_type=%s&card_value=%s;", card.cardType, card.cardValue))
		}

		writeToPlayer(player, fmt.Sprintf("response_type=player_deck&status_code=200&cards=[%s]", buffer.String()[:buffer.Len()-1]))
	} else {
		writeToPlayer(player, "response_type=player_deck&status_code=200&cards=nil")
	}
}

func initAllDecks(game *Game) {
	for index := range game.players {
		initPlayerDeck(&game.players[index], &game.gameDeck)
	}
}

func handleRequest(player *Player, game *Game, index int, data string, lobby *[]net.Conn) {

	if len(data) > 0 {
		if validateData(data, true, "is_alive") {
			sendPing(player)
		} else if validateData(data, true, "leave_game") {
			leaveGame(player, game, index, lobby)
		} else if validateData(data, true, "move_finish") {
			registerMove(player, game, data)
		} else if validateData(data, true, "game_state") {
			sendGameState(player, game)
		} else if validateData(data, true, "player_deck") {
			sendPlayerDeck(player)
		}
	}
}

func registerMove(player *Player, game *Game, data string) {
	var buffer bytes.Buffer

	if !arePlayersEqual(*player, *game.currentPlayer) {
		writeToPlayer(player, "response_type=error&status_code=400&active=true&game_end=false")
		return
	}

	if game.topCard.cardValue == "seven" && !game.topCard.hasBeenUsed {
		drawnCards, newDeck := drawNCards(game.gameDeck, 2)

		for i := 0; i < 2; i++ {
			buffer.WriteString(fmt.Sprintf("card_type=%s&card_value=%s;", drawnCards[i].cardType, drawnCards[i].cardValue))
		}

		writeToPlayer(player, fmt.Sprintf("response_type=move_finish&status_code=200&cards=[%s]&type=seven", buffer.String()[:buffer.Len()-1]))
		game.gameDeck = newDeck
		player.cards = append(player.cards, drawnCards...)
		player.cardCount += 2
		game.topCard.hasBeenUsed = true

		nextPlayer(game)
	} else if game.topCard.cardValue == "ace" && !game.topCard.hasBeenUsed {
		writeToPlayer(player, "response_type=move_finish&status_code=200&cards=nil&type=ace")
		game.topCard.hasBeenUsed = true

		nextPlayer(game)
	} else {
		if !strings.Contains(data, "card") {
			drawnCard, newDeck := drawNCards(game.gameDeck, 1)

			writeToPlayer(player, fmt.Sprintf("response_type=move_finish&status_code=200&card=[card_type=%s&card_value=%s]&type=draw",
				drawnCard[0].cardType, drawnCard[0].cardValue))

			game.gameDeck = newDeck
			player.cards = append(player.cards, drawnCard...)
			player.cardCount++
			nextPlayer(game)
		} else {
			// Getting thrown card
			thrownCard := strings.Split(strings.Split(strings.Split(data, "card=[")[1], "]")[0], "&")
			cardType := strings.Split(thrownCard[0], "=")[1]
			cardValue := strings.Split(thrownCard[1], "=")[1]

			if !doesPlayerHaveCard(*player, Card{cardType, cardValue, false}) ||
				!canCardBePlayed(Card{cardType, cardValue, false}, *game) {

				writeToPlayer(player, "response_type=error&status_code=400&active=true&game_end=false")
				return
			}

			if game.currentCardType != "" {
				game.currentCardType = ""
			}

			if cardValue == "top" && strings.Contains(data, "change") {
				changeType := strings.Split(strings.Split(strings.Split(data, "change")[1], "=")[1], "]")[0]

				if changeType != "leafs" && changeType != "acorns" && changeType != "hearts" && changeType != "bullets" {
					writeToPlayer(player, "response_type=error&status_code=400&active=true&game_end=false")
					return
				}

				game.currentCardType = changeType
			} else {
				game.currentCardType = ""
			}

			writeToPlayer(player, "response_type=move_finish&status_code=200&type=place")
			removePlayerCard(player, Card{cardType, cardValue, false})

			game.throwAwayDeck = append(game.throwAwayDeck, Card{cardType, cardValue, false})
			game.topCard = Card{cardType, cardValue, false}
			nextPlayer(game)
		}
	}
}

func leaveGame(player *Player, game *Game, index int, lobby *[]net.Conn) {
	writeToPlayer(player, "response_type=response_type&status_code=200")

	if player.active {
		connectToLobby(*player, lobby)
	}

	game.players = removePlayer(game.players, index)
}

func sendPing(player *Player) {
	writeToPlayer(player, "response_type=is_alive&status_code=200")
}

func checkReconnect(game *Game) {
	toRemove := make([]int, 0)
	mutex.Lock()

	if len(reconnect) != 0 {
		for index, reconn := range reconnect {
			playerId, err := strconv.Atoi(strings.Split(strings.Split(reconn.request, "player_id")[1], "=")[1])

			if err != nil {
				_ = reconn.conn.Close()
				toRemove = append(toRemove, index)
			} else {
				for _, player := range game.players {
					if player.playerId == playerId {
						_ = player.conn.Close()
						player.conn = reconn.conn
						player.active = true

						toRemove = append(toRemove, index)
					}
				}
			}
		}

		for _, index := range toRemove {
			removeReconnect(reconnect, index)
		}
	}

	mutex.Unlock()
}

func checkResponsive(game Game) bool {
	var playerCount = len(game.players)

	for _, player := range game.players {
		if !player.active {
			playerCount--
		}
	}

	return !(playerCount == 0 || playerCount == 1)
}

func checkDecks(game *Game) {
	if len(game.gameDeck) < 2 {
		game.gameDeck = append(game.gameDeck, game.throwAwayDeck...)
		game.throwAwayDeck = make([]Card, 0)
	}
}

func nextPlayer(game *Game) {
	for i := 1; i < len(game.players); i++ {
		if game.players[(game.currentPlayerIndex+i)%len(game.players)].active {
			game.currentPlayer = &game.players[(game.currentPlayerIndex+i)%len(game.players)]
			game.currentPlayerIndex = (game.currentPlayerIndex + i) % len(game.players)
			return
		}
	}
}

func checkWinner(game *Game) *Player {
	for index, player := range game.players {
		if player.cardCount == 0 {
			return &game.players[index]
		}
	}
	return nil
}

func gameService(game *Game, lobby *[]net.Conn) (error, *Player) {

	initAllDecks(game)

	for {
		checkReconnect(game)

		if !checkResponsive(*game) {
			return errors.New("no_responsive_player"), nil
		}

		checkDecks(game)

		winner := checkWinner(game)
		if winner != nil {
			return nil, winner
		}

		for index, player := range game.players {
			if !player.active {
				continue
			}

			data, err := receiveFromClient(player.conn, GAME_TIME_OUT)

			if err != nil {
				// Check if the error is due to a timeout
				var netErr net.Error
				if errors.As(err, &netErr) && netErr.Timeout() {
					if arePlayersEqual(player, *game.currentPlayer) {
						nextPlayer(game)
					}
				} else {
					game.players[index].active = false

					if arePlayersEqual(player, *game.currentPlayer) {
						nextPlayer(game)
					}
					continue
				}
			}

			handleRequest(&game.players[index], game, index, data, lobby)
		}

	}

}
