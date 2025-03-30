// Получение данных из полей транзакции

package main

import (
	"context"
	"fmt"
	"log"
	"math/big"

	"github.com/ethereum/go-ethereum/ethclient"
)

func getTransactionsInfo(blockID int64) {
	client, err := ethclient.Dial(ethKey)
	if err != nil {
		log.Fatalln(err)
	}

	blockNumber := big.NewInt(blockID)
	block, err := client.BlockByNumber(context.Background(), blockNumber) //get block with this number
	if err != nil {
		log.Fatal(err)
	}

	for _, tx := range block.Transactions() {
		fmt.Println(tx.ChainId())
		fmt.Println(tx.Hash())
		fmt.Println(tx.Value())
		fmt.Println(tx.Cost())
		fmt.Println(tx.To())
		fmt.Println(tx.Gas())
		fmt.Println(tx.GasPrice())

	}
}
