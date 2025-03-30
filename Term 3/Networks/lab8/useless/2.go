// Получение данных из блока по номеру

package main

import (
	"context"
	"log"
	"math/big"

	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"
)

func getBlock(id int64) *types.Block {
	client, err := ethclient.Dial(ethKey)
	if err != nil {
		log.Fatalln(err)
	}

	blockNumber := big.NewInt(id)
	block, err := client.BlockByNumber(context.Background(), blockNumber) //get block with this number
	if err != nil {
		log.Fatal(err)
	}
	return block
}
