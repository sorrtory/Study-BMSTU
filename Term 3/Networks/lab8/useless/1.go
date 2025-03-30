// Получение последнего блока

package main

import (
	"context"
	"fmt"
	"log"
	"math/big"

	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"
)

func getLatestBlock() (*types.Block, *big.Int) {
	client, err := ethclient.Dial(ethKey)
	if err != nil {
		log.Fatalln(err)
	}

	header, err := client.HeaderByNumber(context.Background(), nil)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println(header.Number.String()) // The lastes block in blockchain because nil pointer in header

	blockNumber := big.NewInt(header.Number.Int64())
	block, err := client.BlockByNumber(context.Background(), blockNumber) //get block with this number
	if err != nil {
		log.Fatal(err)
	}

	return block, blockNumber
}
