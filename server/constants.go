package main

const (
	CONN_PORT          = "3333"
	CONN_TYPE          = "tcp"
	MESS_SEPARATOR     = '\n'
	START_CARD_COUNT   = 4
	LOBBY_TIME_OUT     = 15
	GAME_TIME_OUT      = 20
	NEW_CONN_WAIT_TIME = 15
)

func getStartDeck() []Card {
	cardTypes := [4]string{"leafs", "hearts", "acorns", "bullets"}
	cardValues := [8]string{"ace", "king", "bottom", "top", "ten", "nine", "eight", "seven"}
	newDeck := make([]Card, 0)

	for _, cardType := range cardTypes {
		for _, value := range cardValues {
			newDeck = append(newDeck, Card{cardType, value, false})
		}
	}

	return newDeck
}
