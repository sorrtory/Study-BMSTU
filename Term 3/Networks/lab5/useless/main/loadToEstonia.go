package main

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/go-sql-driver/mysql"
)

const (
	username  = "iu9networkslabs"
	password  = "Je2dTYr6"
	hostname  = "students.yss.su"
	dbName    = "iu9networkslabs"
	tableName = "fedukov_lab5"
)

// INSERT INTO `fedukov_lab5` (`header`, `text`)
// VALUES ('ABOBA', 'Текст абобы');

// SELECT * FROM `fedukov_lab5` LIMIT 50

func queryData(db *sql.DB, query string, args ...interface{}) []Info {
	rows, err := db.Query(query, args...)
	if err != nil {
		panic(fmt.Errorf("error executing query: %v", err))
	}

	defer rows.Close()
	out := make([]Info, 0)

	for rows.Next() {
		info := Info{}
		if err := rows.Scan(&info.Id, &info.Header, &info.Text); err != nil {
			panic(fmt.Errorf("error scanning row: %v", err))
		}
		out = append(out, info)
	}

	if err := rows.Err(); err != nil {
		panic(fmt.Errorf("rows error: %v", err))
	}

	return out
}

func queryOneData(db *sql.DB, query string, args ...interface{}) Info {
	rows, err := db.Query(query, args...)
	if err != nil {
		panic(fmt.Errorf("error executing query: %v", err))
	}

	defer rows.Close()
	out := make([]Info, 0)

	for rows.Next() {
		info := Info{}
		if err := rows.Scan(&info.Id, &info.Header, &info.Text); err != nil {
			panic(fmt.Errorf("error scanning row: %v", err))
		}
		out = append(out, info)
	}

	if err := rows.Err(); err != nil {
		panic(fmt.Errorf("rows error: %v", err))
	}

	if len(out) == 0 {
		out = append(out, Info{Header: "NO DATA"})
	}

	return out[0]

}

func insertData(db *sql.DB, info *Info) {
	result, err := db.Exec(fmt.Sprintf("INSERT INTO %s (id, header, text) VALUES (?, ?, ?)", tableName), info.Id, info.Header, info.Text)
	if err != nil {
		panic(fmt.Errorf("error inserting data: %v", err))
	}

	rowsAffected, err := result.LastInsertId()
	if err != nil {
		panic(fmt.Errorf("error getting last insert id: %v", err))
	}
	fmt.Printf("Inserted: %+v (%d times)\n", info, rowsAffected)

}

func updateData(db *sql.DB, info *Info) {
	result, err := db.Exec(fmt.Sprintf("UPDATE %s SET header = ?, text = ? WHERE id = ?", tableName), info.Header, info.Text, info.Id)
	if err != nil {
		panic(fmt.Errorf("error updating data: %v", err))
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		panic(fmt.Errorf("error getting affected rows: %v", err))
	}
	fmt.Printf("Updated: %+v (%d times)\n", info, rowsAffected)

}

func deleteData(db *sql.DB, info *Info) {
	result, err := db.Exec(fmt.Sprintf("DELETE FROM %s WHERE id = ?", tableName), info.Id)
	if err != nil {
		panic(fmt.Errorf("error deleting data: %v", err))
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		panic(fmt.Errorf("error getting affected rows: %v", err))
	}
	fmt.Printf("Deleted: %+v (%d times)\n", info, rowsAffected)
}

func fitInTable(db *sql.DB, info *Info) {
	oldInfo := queryData(db, fmt.Sprintf("select * from %s WHERE id = ?", tableName), info.Id)

	switch len(oldInfo) {
	case 0:
		insertData(db, info)
	case 1:
		updateData(db, info)
	default:
		deleteData(db, info)
		insertData(db, info)
	}
}

func loadToEstonia(infos *[]Info) {
	log.Println("Process database")

	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s)/%s", username, password, hostname, dbName))
	if err != nil {
		panic(err.Error())
	}

	// Verify the connection
	if err := db.Ping(); err != nil {
		panic(fmt.Errorf("error connecting to database: %v", err))
	}

	for _, v := range *infos {
		fitInTable(db, &v)
	}

	// updateData(db, Info{1, "Alice", "ssasassas"})
	// deleteData(db, Info{Id: 2})
	// out := queryData(db, fmt.Sprintf("select * from %s WHERE id = ?", tableName), 1)
	// fmt.Println(out)

	defer db.Close()
	// fmt.Println("Success!")
}

func getFromEstonia(infos *[]Info) {
	log.Println("Process database")

	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(%s)/%s", username, password, hostname, dbName))
	if err != nil {
		panic(err.Error())
	}

	// Verify the connection
	if err := db.Ping(); err != nil {
		panic(fmt.Errorf("error connecting to database: %v", err))
	}

	// for i, _ := range *infos {
	// 	// fitInTable(db, &v)
	// 	(*infos)[i] = queryData(db, fmt.Sprintf("select * from %s", tableName))
	// }
	*infos = queryData(db, fmt.Sprintf("select * from %s", tableName))
	// *infos = queryData(db, fmt.Sprintf("select * from %s WHERE id = ?", tableName), info.Id)
	// updateData(db, Info{1, "Alice", "ssasassas"})
	// deleteData(db, Info{Id: 2})
	// out := queryData(db, fmt.Sprintf("select * from %s WHERE id = ?", tableName), 1)
	// fmt.Println(out)

	defer db.Close()
	// fmt.Println("Success!")
}
