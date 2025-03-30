package main

import (
	"encoding/json"
	"fmt"
	"os"
)

type User struct {
	Login    string `json:"login"`
	Password string `json:"password"`
}

func writeJSON(filePath string, data interface{}) error {
	jsonData, err := json.MarshalIndent(data, "", "    ")
	if err != nil {
		return err
	}

	return os.WriteFile(filePath, jsonData, 0644)
}

func readJSON(filePath string, data interface{}) error {
	jsonData, err := os.ReadFile(filePath)
	if err != nil {
		return err
	}

	return json.Unmarshal(jsonData, data)
}

func checkUserPasswd(lgn string, psswd string) bool {
	var users []User
	if err := readJSON(WORKING_FOLDER+USER_LOGIN_FILE, &users); err != nil {
		fmt.Println("Error reading JSON:", err)
		return false
	}

	for _, user := range users {
		if user.Login == lgn && user.Password == psswd {
			return true
		}
	}
	return false

}
