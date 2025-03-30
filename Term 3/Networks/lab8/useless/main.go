package main

import (
	"context"
	"fmt"
	"math/big"
	"time"

	"firebase.google.com/go/v4/db"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
)

var ethKey = "https://mainnet.infura.io/v3/ce09af264e6f4ef4a930b4037c908465"
var DB *db.Ref

func sendData(data interface{}) {
	DB.Set(context.Background(), data)
	fmt.Printf("Sended data: [%v]", data)
}

func hasBlock(blockID string) bool {
	blocks, err := DB.OrderByKey().GetOrdered(context.Background())
	if err != nil {
		fmt.Errorf("Bad blocks: %v", err)
	}

	for _, v := range blocks {
		if v.Key() == blockID {
			return true
		}
	}

	return false
}

type Block struct {
	BlockID           uint64 `json:"BlockID"`
	Time              uint64 `json:"Time"`
	Difficulty        uint64 `json:"Difficulty"`
	Hash              string `json:"Hash"`
	TransactionNumber int    `json:"TransactionNumber"`
}

type Transaction struct {
	ChainId  *big.Int        `json:"ChainId"`
	Hash     common.Hash     `json:"Hash"`
	Value    *big.Int        `json:"Value"`
	Cost     *big.Int        `json:"Cost"`
	To       *common.Address `json:"To"`
	Gas      uint64          `json:"Gas"`
	GasPrice *big.Int        `json:"GasPrice"`
}

func getInfoFromBlock(block *types.Block) {
	// all info about block
	blockID := block.Number().Uint64()
	DB = DB.Child(fmt.Sprintf("Block-%v", blockID)).Child("Info")

	sendData(Block{
		BlockID:           blockID,
		Time:              block.Time(),
		Difficulty:        block.Difficulty().Uint64(),
		Hash:              block.Hash().Hex(),
		TransactionNumber: len(block.Transactions()),
	})

	DB = DB.Parent().Child("Transactions")

	for i, tx := range block.Transactions() {
		DB = DB.Child(fmt.Sprintf("Transaction-%v", i))
		sendData(Transaction{
			ChainId:  tx.ChainId(),
			Hash:     tx.Hash(),
			Value:    tx.Value(),
			Cost:     tx.Cost(),
			To:       tx.To(),
			Gas:      tx.Gas(),
			GasPrice: tx.GasPrice(),
		})

		DB = DB.Parent()
	}

	DB = DB.Parent().Parent()
}

func main() {
	DB = connectDB()
	clearDB(DB)
	for {
		fmt.Println("Check blocks")
		block, id := getLatestBlock()
		if hasBlock(id.String()) {
			fmt.Println("Has block!")
		} else {
			fmt.Println("Add block")
			getInfoFromBlock(block)
		}
		 
		time.Sleep(time.Second * 2)
	}
}
