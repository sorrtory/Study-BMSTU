package main
import "os"
/* Example urls
http://127.0.0.1:1818/?url=http://gnuplot.info

http://gnuplot.info/
https://netlib.sandia.gov/
https://putty.org/
https://www.openbsd.org/
https://netbsd.org/
https://www.freebsd.org/
*/

var SERVER_ADDRESS = os.Getenv("MyIP")

var SERVER_PORT = "1819"
var SERVER = SERVER_ADDRESS + ":" + SERVER_PORT

func main() {
	startServer()
}
