package main

import (
	"fmt"
	"io"
	"log"
	"net/url"
	"path/filepath"

	// fuck the "golang.org/x/net/html"
	"github.com/PuerkitoBio/goquery"
	"github.com/cavaliergopher/grab/v3"
)

// changeURL add "link" to "attrLink" via SERVER proxy if needed
func changeURL(link string, attrLink string) string {
	parsed_attrLink, err := url.Parse(attrLink)
	if err != nil {
		log.Fatalf("Failed to parse URL: %s\n", err)
		return ""
	}

	parsed_link, err := url.Parse(link)
	if err != nil {
		log.Fatalf("Failed to parse URL: %s\n", err)
		return ""
	}

	// Set file location
	d := filepath.Dir(parsed_link.Path)
	if d[len(d)-1] != '/' {
		d += "/"
	}
	parsed_link.Path = d

	// Check for file format
	// ext := filepath.Ext(parsed_attrLink.Path)
	// if ext != "" && ext != ".html" {
	// 	// Don't proxy
	// 	// i.e. keep img, css, js, ... links

	// 	// Amend local paths
	// 	if parsed_attrLink.IsAbs() {
	// 		return attrLink
	// 	} else {
	// 		return parsed_link.String() + attrLink
	// 	}
	// } else {
	// 	// Do proxy

	// 	// Amend local paths
	// 	if parsed_attrLink.IsAbs() {
	// 		return fmt.Sprintf("http://%s?url=%s", SERVER, attrLink)
	// 	} else {
	// 		return fmt.Sprintf("http://%s?url=%s", SERVER, parsed_link.String() + attrLink)
	// 	}
	// }

	// Amend local paths
	if parsed_attrLink.IsAbs() {
		return fmt.Sprintf("http://%s?url=%s", SERVER, attrLink)
	} else {
		return fmt.Sprintf("http://%s?url=%s", SERVER, parsed_link.String()+attrLink)
	}
}

func makeLinkAbsolute(link string, server string) string {
	parsed_link, err := url.Parse(link)
	if err != nil {
		log.Fatalf("Failed to parse URL: %s\n", err)
		return ""
	}

	server_link, err := url.Parse(server)
	if err != nil {
		log.Fatalf("Failed to parse URL: %s\n", err)
		return ""
	}

	server_link.Path = ""

	// Amend local paths
	if parsed_link.IsAbs() {
		return link
	} else {
		return fmt.Sprintf(server_link.String() + "/" + link)
	}
}

// source and link from [http.Get](link)
func parsedHTML(source io.Reader, link string) string {

	// Load the HTML document using goquery
	doc, err := goquery.NewDocumentFromReader(source)
	if err != nil {
		log.Fatal("no gq\n", err)
		return ""
	}

	// Parse document
	doc.Find("iframe").Each(func(i int, s *goquery.Selection) {
		param := "src"
		v, exists := s.Attr(param)
		if exists {
			s.SetAttr(param, changeURL(link, v))
		}
	})

	doc.Find("img").Each(func(i int, s *goquery.Selection) {
		param := "src"
		v, exists := s.Attr(param)
		if exists {
			aboba := makeLinkAbsolute(v, link)
			fmt.Println(aboba)
			resp, err := grab.Get("./site/", aboba)
			if err != nil {
				log.Println(err)
			}
			fmt.Println("Download saved to", resp.Filename)

			s.SetAttr(param, fmt.Sprintf("http://%s/%s", SERVER, resp.Filename))
		}
	})

	doc.Find("link").Each(func(i int, s *goquery.Selection) {
		param := "href"
		v, exists := s.Attr(param)
		if exists {
			resp, err := grab.Get("./site/", makeLinkAbsolute(v, link))
			if err != nil {
				log.Println(err)
			}
			fmt.Println("Download saved to", resp.Filename)

			s.SetAttr(param, fmt.Sprintf("http://%s/%s", SERVER, resp.Filename))
		}
	})

	doc.Find("a").Each(func(i int, s *goquery.Selection) {
		param := "href"
		v, exists := s.Attr(param)
		if exists {
			s.SetAttr(param, changeURL(link, v))
		}
	})

	// Convert the modified document back to HTML
	html, err := doc.Html()
	if err != nil {
		log.Fatal("no inj", err)
		return ""
	}
	return html
}
