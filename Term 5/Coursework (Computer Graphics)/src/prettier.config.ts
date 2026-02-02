import { type Config } from "prettier"

const config: Config = {
    trailingComma: "none",
    semi: false,
    singleQuote: false,
    tabWidth: 2,
    overrides: [
        {
            files: ["*.js", "*.ts", "*.html"],
            options: {
                tabWidth: 4
            }
        }
    ]
}

export default config
