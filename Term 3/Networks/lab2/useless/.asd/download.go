package main

import (
	// "fmt"
	"net/http"

	log "github.com/mgutz/logxi/v1"
	"golang.org/x/net/html"
)

func getAttr(node *html.Node, key string) string {
	for _, attr := range node.Attr {
		if attr.Key == key {
			return attr.Val
		}
	}
	return ""
}

func getChildren(node *html.Node) []*html.Node {
	var children []*html.Node
	for c := node.FirstChild; c != nil; c = c.NextSibling {
		children = append(children, c)
	}
	return children
}

func isElem(node *html.Node, tag string) bool {
	return node != nil && node.Type == html.ElementNode && node.Data == tag
}

func isDiv(node *html.Node, class string) bool {
	return isElem(node, "div") && getAttr(node, "class") == class
}

type Link struct {
	Ref, Text string
}

func getLink(node *html.Node, link *Link) {
	if node != nil {
		for c := node.FirstChild; c != nil; c = c.NextSibling {
			// if isElem(c, "h3") && getAttr(c, "class") == "title " {
			// 	for cc := c.FirstChild; cc != nil; cc = cc.NextSibling {
			// 		if isElem(cc, "a") {
			// 			link.Ref = getAttr(cc, "href")
			// 			if link.Ref[0] == '/' {
			// 				link.Ref = "https:" + link.Ref
			// 			}
			// 			link.Text = cc.FirstChild.Data
			// 		}

			// 	}

			if isElem(c, "a") {
				link.Ref = getAttr(c, "href")
				if link.Ref[0] == '/' {
					link.Ref = "https:" + link.Ref
				}
				if isDiv(c.FirstChild, "related-body") {
					link.Text = "WATCH LIVE: " + c.FirstChild.LastChild.Data

				} else {
					link.Text = c.FirstChild.Data
				}

			} else {
				getLink(c, link)
			}
		}
	}
}

type Pic struct {
	Src, W, H, Alt string
}

func getPic(node *html.Node, pic *Pic) {
	if node != nil {
		for c := node.FirstChild; c != nil; c = c.NextSibling {

			if isElem(c, "img") {
				pic.Src = "https:" + getAttr(c, "src")
				pic.W = getAttr(c, "width")
				pic.H = getAttr(c, "height")
				pic.Alt = getAttr(c, "alt")
			} else if isElem(c, "video") {

				cc := c.FirstChild.NextSibling
				pic.Alt = "VIDEO"
				pic.Src = getAttr(cc, "src")
				pic.W = getAttr(cc, "type")

			} else if isElem(c, "iframe") {

				// cc := c.FirstChild.NextSibling

				// pic.Alt = "IFRAME"
				// pic.Src = getAttr(cc, "src")
				// fmt.Println(c.Attr)

			} else {
				getPic(c, pic)
			}
		}
	}
}

type Item struct {
	Pic  Pic
	Link Link
}

var ITEMS []*Item

func search(node *html.Node) {
	if isElem(node, "article") {
		var pic Pic
		var link Link
		for c := node.FirstChild; c != nil; c = c.NextSibling {
			// pic
			if isDiv(c, "m") || isDiv(c, "m ") {
				if pic.Src != "" {
					panic("PIC")
				}
				getPic(c, &pic)
			}
			// link
			if isDiv(c, "info ") || isDiv(c, "info") {
				if link.Text != "" {
					panic("LINK")
				}
				getLink(c, &link)
			}
		}
		if pic != (Pic{}) && link != (Link{}) {
			ITEMS = append(ITEMS, &Item{pic, link})
		}
	}

	for c := node.FirstChild; c != nil; c = c.NextSibling {
		search(c)
	}
}

func downloadNews() []*Item {
	log.Info("sending request to foxnews.com")
	if response, err := http.Get("https://www.foxnews.com/"); err != nil {
		log.Error("request to foxnews.com failed", "error", err)
	} else {
		defer response.Body.Close()
		status := response.StatusCode
		log.Info("got response from foxnews.com", "status", status)
		if status == http.StatusOK {
			if doc, err := html.Parse(response.Body); err != nil {
				log.Error("invalid HTML from foxnews.com", "error", err)
			} else {
				log.Info("HTML from foxnews.com parsed successfully")
				search(doc)
				return ITEMS
			}
		}
	}
	return nil
}

// func main() {

// 	downloadNews()

// 	// downloadNews()
// }
