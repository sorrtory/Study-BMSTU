Видео по блокчеин: https://dzen.ru/video/watch/6378fcc2be4db80030f20c8e

Шлюз: https://www.infura.io/
login: danila@posevin.com
passwd: BMSTU1bmstu1
https://mainnet.infura.io/v3/8133ff0c11dc491daac3f680d2f74d18
Посмотреть список блоков https://etherscan.io/
Инструкция для Go: https://goethereumbook.org/en/
Библиотека: https://github.com/ethereum/go-ethereum
Firebase: https://github.com/firebase/firebase-admin-go
Дополнительно: почта на блокчейне: https://www.ixbt.com/live/crypto/pervaya-web-30-pochta-na-blokcheyne-ethereum-registriruemsya-i-poluchaem-ranniy-dostup.html


##############################
# Получение последнего блока #
##############################

package main

import (
  "context"
  "fmt"
  "github.com/ethereum/go-ethereum/ethclient"
  "log"
  "math/big"
)

func main() {
  client, err := ethclient.Dial("https://mainnet.infura.io/v3/8133ff0c11dc491daac3f680d2f74d18")
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

  // all info about block
  fmt.Println(block.Number().Uint64())
  fmt.Println(block.Time())
  fmt.Println(block.Difficulty().Uint64())
  fmt.Println(block.Hash().Hex())
  fmt.Println(len(block.Transactions()))
}

#######################################
# Получение данных из блока по номеру #
#######################################

package main

import (
  "context"
  "fmt"
  "github.com/ethereum/go-ethereum/ethclient"
  "log"
  "math/big"
)

func main() {
  client, err := ethclient.Dial("https://mainnet.infura.io/v3/8133ff0c11dc491daac3f680d2f74d18")
  if err != nil {
    log.Fatalln(err)
  }

  blockNumber := big.NewInt(15960495)
  block, err := client.BlockByNumber(context.Background(), blockNumber) //get block with this number
  if err != nil {
    log.Fatal(err)
  }

  // all info about block
  fmt.Println(block.Number().Uint64())
  fmt.Println(block.Time())
  fmt.Println(block.Difficulty().Uint64())
  fmt.Println(block.Hash().Hex())
  fmt.Println(len(block.Transactions()))
}


########################################
# Получение данных из полей транзакции #
########################################
package main

import (
  "context"
  "fmt"
  "github.com/ethereum/go-ethereum/ethclient"
  "log"
  "math/big"
)

func main() {
  client, err := ethclient.Dial("https://mainnet.infura.io/v3/8133ff0c11dc491daac3f680d2f74d18")
  if err != nil {
    log.Fatalln(err)
  }

  blockNumber := big.NewInt(15960495)
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