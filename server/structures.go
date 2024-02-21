package main

import "net"

type Player struct {
	conn      net.Conn
	playerId  int
	cardCount int
	cards     []Card
	active    bool
}

type Card struct {
	cardType    string
	cardValue   string
	hasBeenUsed bool
}

type Game struct {
	players            []Player
	currentPlayer      *Player
	currentPlayerIndex int
	topCard            Card
	throwAwayDeck      []Card
	gameDeck           []Card
	currentCardType    string
}

type Reconnect struct {
	request string
	conn    net.Conn
}
