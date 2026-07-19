var RULES = {
    "C": {
        "Regs" : {
            "Whites" : [/[ \t\n\r]+/g],
            "Hex" : [/\b0x[0-9A-Fa-f]+\b/g],
            "Octo" : [/\b0[0-7]+\b/g],
            "Double" : [/\b(0|[1-9][0-9]*)\.[0-9]*\b|\b\.[0-9]+\b/g],
            "Integer" : [/\b0\b|\b[1-9][0-9]*[uUlL]*\b/g],
            "Comment" : [/\/\/.*/g, /\/\*.*\*\//g],
            "String" : [/'((?:\\[\s\S]|[^'\\])*)'/g, /"((?:\\[\s\S]|[^"\\])*)"/g, /`((?:\\[\s\S]|[^`\\])*)`/g],
            "IncludeStr" : [/&lt;.*&gt;\s*\n/g],
            "Angles" : [/&lt;/g, /&gt;/g],
            "Include" : [/#include\b/g],
            "Hashed" : [/#.*[;]?/g],
            "Keywords" : [/\band\b/g, /\bauto\b/g, /\b_Bool\b/g, 
            /\bbool\b/g, /\bbreak\b/g, /\bcase\b/g, /\bchar\b/g,
            /\bconst\b/g, /\bcontinue\b/g, /\bdefault\b/g, /\bdo\b/g, 
            /\bdouble\b/g, /\belse\b/g, /\benum\b/g, /\bextern\b/g, 
            /\bfloat\b/g, /\bfor\b/g, /\bgoto\b/g, /\bif\b/g, /\binline\b/g, 
            /\bint\b/g, /\bint8_t\b/g, /\bint16_t\b/g, /\bint32_t\b/g, 
            /\bint64_t\b/g, /\blong\b/g, /\bll\b/g, /\blu\b/g, /\bor\b/g, 
            /\bnot\b/g, /\bregister\b/g, /\brestrict\b/g, /\breturn\b/g, 
            /\bshort\b/g, /\bsigned\b/g, /\bsizeof\b/g, /\bstatic\b/g, 
            /\bstruct\b/g, /\bsize_t\b/g, /\bswitch\b/g, /\btypedef\b/g, 
            /\bunion\b/g, /\bunsigned\b/g, /\buint8_t\b/g, /\buint16_t\b/g, 
            /\buint32_t\b/g, /\buint64_t\b/g, /\bul\b/g, /\bull\b/g, /\bvoid\b/g, 
            /\bvolatile\b/g, /\bwhile\b/g, /\btrue\b/g, /\bfalse\b/g, 
            /\bYES\b/g, /\bNO\b/g, /\bNULL\b/g],
            "Word" : [/[a-zA-Z0-9_]+/g],
            "Symbol" : [/./g]
        },
        "Color": {
            "Comment" : "green",
            "String" : "orange",
            "IncludeStr" : "orange",
            "Include" : "blue",
            "Keywords": "blue",
            "Hashed" : "blue",
            "Integer" : "lime",
            "Double" : "lime",
            "Hex" : "lime",
            "Octo" : "lime"

        },
        "Multi": {
            "Order": ["brown", "blue", "purple"],
            "Triggers": ["(", ")", "[", "]", "{", "}"]
        },
        "Indent": {               
            "Plus" : ["(", "[", "{", "<"],
            "Sign" : "  ",
            "Value" : 2
        }
    },
    "C++": {
        "Regs" : {
            "Whites" : [/[ \t\n\r]+/g],
            "Hex" : [/\b0x[0-9A-Fa-f]+\b/g],
            "Octo" : [/\b0[0-7]+\b/g],
            "Double" : [/\b(0|[1-9][0-9]*)\.[0-9]*\b|\b\.[0-9]+\b/g],
            "Integer" : [/\b0\b|\b[1-9][0-9]*\b/g],
            "Comment" : [/\/\/.*/g, /\/\*.*\*\//g],
            "String" : [/'((?:\\[\s\S]|[^'\\])*)'/g, /"((?:\\[\s\S]|[^"\\])*)"/g, /`((?:\\[\s\S]|[^`\\])*)`/g],
            "IncludeStr" : [/&lt;.*&gt;\n/g],
            "Angles" : [/&lt;/g, /&gt;/g],
            "Include" : [/#include\b/g],
            "Hashed" : [/#.*[;]?/g],
            "Keywords" : [/\band\b/g, /\bauto\b/g, /\b_Bool\b/g, 
            /\bbool\b/g, /\bbreak\b/g, /\bcase\b/g, /\bchar\b/g,
            /\bconst\b/g, /\bcontinue\b/g, /\bdefault\b/g, /\bdo\b/g, 
            /\bdouble\b/g, /\belse\b/g, /\benum\b/g, /\bextern\b/g, 
            /\bfloat\b/g, /\bfor\b/g, /\bgoto\b/g, /\bif\b/g, /\binline\b/g, 
            /\bint\b/g, /\bint8_t\b/g, /\bint16_t\b/g, /\bint32_t\b/g, 
            /\bint64_t\b/g, /\blong\b/g, /\bll\b/g, /\blu\b/g, /\bor\b/g, 
            /\bnot\b/g, /\bregister\b/g, /\brestrict\b/g, /\breturn\b/g, 
            /\bshort\b/g, /\bsigned\b/g, /\bsizeof\b/g, /\bstatic\b/g, 
            /\bstruct\b/g, /\bsize_t\b/g, /\bswitch\b/g, /\btypedef\b/g, 
            /\bunion\b/g, /\bunsigned\b/g, /\buint8_t\b/g, /\buint16_t\b/g, 
            /\buint32_t\b/g, /\buint64_t\b/g, /\bul\b/g, /\bull\b/g, /\bvoid\b/g, 
            /\bvolatile\b/g, /\bwhile\b/g, /\btrue\b/g, /\bfalse\b/g, 
            /\bYES\b/g, /\bNO\b/g, /\bNULL\b/g, /\balignas\b/g, /\balignof\b/g, 
            /\band_eg\b/g, /\basm\b/g, /\bbitand\b/g, /\bbitor\b/g, /\bcatch\b/g, 
            /\bclass\b/g, /\bcompl\b/g, /\bconcept\b/g, /\bconsteval\b/g, 
            /\bconstexpr\b/g, /\bconstinit\b/g, /\bconst_cast\b/g, /\bco_await\b/g, 
            /\bco_return\b/g, /\bco_yield\b/g, /\bdecltype\b/g, /\bdelete\b/g, 
            /\bdynamic_cast\b/g, /\bexport\b/g, /\bexplicit\b/g, /\bfriend\b/g, 
            /\bmutable\b/g, /\bnamespace\b/g, /\bnoexcept\b/g, /\bnot_eq\b/g, 
            /\bnullptr\b/g, /\boperator\b/g, /\bor_eq\b/g, /\bprivate\b/g, 
            /\bprotected\b/g, /\bpublic\b/g, /\breflexpr\b/g,
            /\breinterpret_cast\b/g, /\brequires\b/g, /\bstatic_assert\b/g, 
            /\bstatic_cast\b/g, /\btemplate\b/g, /\bthis\b/g, /\bthread_local\b/g, 
            /\bthrow\b/g, /\btry\b/g, /\btypeid\b/g, /\btypename\b/g, /\busing\b/g, 
            /\bvirtual\b/g, /\bwchar_t\b/g, /\bxor\b/g, /\bxor_eq\b/g, /\bfinal\b/g, 
            /\boverride\b/g, /\bimport\b/g, /\bmodule\b/g, /\b_Pragma\b/g],
            "Word" : [/[a-zA-Z0-9_]+/g],
            "Symbol" : [/./g]
        },
        "Color": {
            "Comment" : "green",
            "String" : "orange",
            "IncludeStr" : "orange",
            "Include" : "blue",
            "Keywords": "blue",
            "Hashed" : "blue",
            "Integer" : "lime",
            "Double" : "lime",
            "Hex" : "lime",
            "Octo" : "lime"

        },
        "Multi": {
            "Order": ["brown", "blue", "purple"],
            "Triggers": ["(", ")", "[", "]", "{", "}"]
        },
        "Indent": {               
            "Plus" : ["(", "[", "{", "<"],
            "Sign" : "\t",
            "Value" : 2
        }
    },
    "Go": {
        "Regs" : {
            "Whites" : [/[ \t\n\r]+/g],
            "Hex" : [/\b0x[0-9A-Fa-f]+\b/g],
            "Octo" : [/\b0[0-7]+\b/g],
            "Double" : [/\b(0|[1-9][0-9]*)\.[0-9]*\b|\b\.[0-9]+\b/g],
            "Integer" : [/\b0\b|\b[1-9][0-9]*\b/g],
            "Comment" : [/\/\/.*/g, /\/\*.*\*\//g],
            "String" : [/'((?:\\[\s\S]|[^'\\])*)'/g, /"((?:\\[\s\S]|[^"\\])*)"/g, /`((?:\\[\s\S]|[^`\\])*)`/g],
            "Angles" : [/&lt;/g, /&gt;/g],
            "Keywords" : [/\bbreak\b/g, /\bcase\b/g, /\bchan\b/g, /\bconst\b/g, /\bcontinue\b/g, 
            /\bdefault\b/g, /\bdefer\b/g, /\belse\b/g, /\bfallthrough\b/g, /\bfor\b/g,
            /\bfunc\b/g, /\bgo\b/g, /\bgoto\b/g, /\bif\b/g, /\bimport\b/g, /\binterface\b/g, 
            /\bmap\b/g, /\bpackage\b/g, /\brange\b/g, /\breturn\b/g, /\bselect\b/g, 
            /\bstruct\b/g, /\bswitch\b/g, /\btype\b/g, /\bvar\b/g,
            /\bu?int(8|16|32|64)?\b/g, /\bfloat(32|64)\b/g, /\bbyte\b/g, /\brune\b/g,
            /\buintptr\b/g, /\bcomplex(32|64)\b/g,
            /\btrue\b/g, /\bfalse\b/,
            ],
            "Word" : [/[a-zA-Z0-9_]+/g],
            "Symbol" : [/./g]
        },
        "Color" : {
            "Comment" : "green",
            "String" : "orange",
            "Keywords": "blue",
            "Integer" : "lime",
            "Double" : "lime",
            "Hex" : "lime",
            "Octo" : "lime"
        },
        "Multi" : {
            "Order": ["brown", "blue", "purple"],
            "Triggers": ["(", ")", "[", "]", "{", "}"]
        },
        "Indent" : {
            "Plus" : ["(", "[", "{", "<"],
            "Sign" : "\t",
            "Value" : 4
        }
    },
    "Python": {
        "Regs" : {},
        "Color" : {},
        "Multi" : {
            "Order" : [],
            "Triggers" : []
        },
        "Indent" : {
            "Plus" : [],
            "Sign" : "",
            "Value" : 1
        }
    },
    "Java": {
        "Regs" : {
            "Whites" : [/[ \t\n\r]+/g],
            "Hex" : [/\b0x[0-9A-Fa-f]+\b/g],
            "Octo" : [/\b0[0-7]+\b/g],
            "Double" : [/\b(0|[1-9][0-9]*)\.[0-9]*\b|\b\.[0-9]+\b/g],
            "Integer" : [/\b0\b|\b[1-9][0-9]*\b/g],
            "Comment" : [/\/\/.*/g, /\/\*.*\*\//g],
            "String" : [/'((?:\\[\s\S]|[^'\\])*)'/g, /"((?:\\[\s\S]|[^"\\])*)"/g, /`((?:\\[\s\S]|[^`\\])*)`/g],
            "Angles" : [/&lt;/g, /&gt;/g],
            "Keywords" : [/\babstract\b/g, /\bassert\b/g, /\bboolean\b/g, /\bbreak\b/g, /\bbyte\b/g, 
            /\bcase\b/g, /\bcatch\b/g, /\bchar\b/g, /\bclass\b/g, /\bcontinue\b/g, /\bdefault\b/g, /\bdo\b/g, 
            /\bdouble\b/g, /\belse\b/g, /\benum\b/g, /\bextends\b/g, /\bfalse\b/g, /\bfinal\b/g, /\bfinally\b/g, 
            /\bfloat\b/g, /\bfor\b/g, /\bif\b/g, /\bimplements\b/g, /\bimport\b/g, /\binstanceof\b/g, /\bint\b/g, 
            /\binterface\b/g, /\blong\b/g, /\bnative\b/g, /\bnew\b/g, /\bnull\b/g, /\bpackage\b/g, /\bprivate\b/g, 
            /\bprotected\b/g, /\bpublic\b/g, /\breturn\b/g, /\bshort\b/g, /\bstatic\b/g, /\bstrictfp\b/g, 
            /\bsuper\b/g, /\bswitch\b/g, /\bsynchronized\b/g, /\bthis\b/g, /\bthrow\b/g, /\bthrows\b/g, 
            /\btransient\b/g, /\btrue\b/g, /\btry\b/g, /\bvoid\b/g, /\bvolatile\b/g, /\bwhile\b/g],
            "Word" : [/[a-zA-Z0-9_]+/g],
            "Symbol" : [/./g]
        },
        "Color" : {
            "Comment" : "green",
            "String" : "orange",
            "Keywords": "blue",
            "Integer" : "lime",
            "Double" : "lime",
            "Hex" : "lime",
            "Octo" : "lime"
        },
        "Multi" : {
            "Order": ["brown", "blue", "purple"],
            "Triggers": ["(", ")", "[", "]", "{", "}"]
        },
        "Indent" : {
            "Plus" : ["(", "[", "{", "<"],
            "Sign" : "\t",
            "Value" : 2
        }
    },
    "Scheme": {
        "Regs" : {
            "Whites" : [/[ \t\n\r]+/g],
            "Double" : [/(\b(0|[1-9][0-9]*)\.[0-9]*(e[0-9]+)?\b)|(\b\.[0-9]+(e[0-9]+)?\b)/g],
            "Integer" : [/\b[0-9]+\b/g],
            "Comment" : [/[;]+.*(\n|$)/g],
            "String" : [/"((?:\\[\s\S]|[^"\\])*)"/g],
            "Angles" : [/&lt;/g, /&gt;/g],
            "Keywords" : [/\bcase-lambda\b/g, /\bcall\/cc\b/g, /\bclass\b/g, /\bdefine-class\b/g, /\bexit-handler\b/g, 
            /\bfield\b/g, /\bimport\b/g, /\binherit\b/g, /\binit-field\b/g, /\binterface\b/g, /\blet\*-values\b/g, 
            /\blet-values\b/g, /\blet\/ec\b/g, /\bmixin\b/g, /\bopt-lambda\b/g, /\boverride\b/g, /\bprotect\b/g, 
            /\bprovide\b/g, /\bpublic\b/g, /\brename\b/g, /\brequire\b/g, /\brequire-for-syntax\b/g, /\bsyntax\b/g, 
            /\bsyntax-case\b/g, /\bsyntax-error\b/g, /\bunit\/sig\b/g, /\bunless\b/g, /\bwhen\b/g, /\bwith-syntax\b/g, 
            /\band\b/g, /\bbegin\b/g, /\bcall-with-current-continuation\b/g, /\bcall-with-input-file\b/g, 
            /\bcall-with-output-file\b/g, /\bcase\b/g, /\bcond\b/g, /\bdefine\b/g, /\bdefine-syntax\b/g, /\bdelay\b/g, 
            /\bdo\b/g, /\bdynamic-wind\b/g, /\belse\b/g, /\bfor-each\b/g, /\bif\b/g, /\blambda\b/g, /\blet\b/g, 
            /\blet\*\b/g, /\blet-syntax\b/g, /\bletrec\b/g, /\bletrec-syntax\b/g, /\bmap\b/g, /\bor\b/g, 
            /\bsyntax-rules\b/g, /\babs\b/g, /\bacos\b/g, /\bangle\b/g, /\bappend\b/g, /\bapply\b/g, /\basin\b/g, 
            /\bassoc\b/g, /\bassq\b/g, /\bassv\b/g, /\batan\b/g, /\bboolean\?\b/g, /\bcaar\b/g, /\bcadr\b/g, 
            /\bcall-with-values\b/g, /\bcar\b/g, /\bcdddar\b/g, /\bcdr\b/g, /\bcddddr\b/g, /\bceiling\b/g, 
            /\bchar-&gt;integer\b/g, /\bchar-alphabetic\?\b/g, /\bchar-ci&lt;=\?\b/g, /\bchar-ci&lt;\?\b/g, /\bchar-ci=\?\b/g, 
            /\bchar-ci&gt;=\?\b/g, /\bchar-ci&gt;\?\b/g, /\bchar-downcase\b/g, /\bchar-lower-case\?\b/g, /\bchar-numeric\?\b/g, 
            /\bchar-ready\?\b/g, /\bchar-upcase\b/g, /\bchar-upper-case\?\b/g, /\bchar-whitespace\?\b/g, /\bchar&lt;=\?\b/g, 
            /\bchar&lt;\?\b/g, /\bchar=\?\b/g, /\bchar&gt;=\?\b/g, /\bchar&gt;\?\b/g, /\bchar\?\b/g, /\bclose-input-port\b/g, 
            /\bclose-output-port\b/g, /\bcomplex\?\b/g, /\bcons\b/g, /\bcos\b/g, /\bcurrent-input-port\b/g, 
            /\bcurrent-output-port\b/g, /\bdenominator\b/g, /\bdisplay\b/g, /\beof-object\?\b/g, /\beq\?\b/g, 
            /\bequal\?\b/g, /\beqv\?\b/g, /\beval\b/g, /\beven\?\b/g, /\bexact-&gt;inexact\b/g, /\bexact\?\b/g, /\bexp\b/g, 
            /\bexpt\b/g, /\b#f\b/g, /\bfloor\b/g, /\bforce\b/g, /\bgcd\b/g, /\bimag-part\b/g, 
            /\binexact-&gt;exact\b/g, /\binexact\?\b/g, /\binput-port\?\b/g, /\binteger-&gt;char\b/g, 
            /\binteger\?\b/g, /\binteraction-environment\b/g, /\blcm\b/g, /\blength\b/g, /\blist\b/g, /\blist-&gt;string\b/g, 
            /\blist-&gt;vector\b/g, /\blist-ref\b/g, /\blist-tail\b/g, /\blist\?\b/g, /\bload\b/g, /\blog\b/g, 
            /\bmagnitude\b/g, /\bmake-polar\b/g, /\bmake-rectangular\b/g, /\bmake-string\b/g, /\bmake-vector\b/g, 
            /\bmax\b/g, /\bmember\b/g, /\bmemq\b/g, /\bmemv\b/g, /\bmin\b/g, /\bmodulo\b/g, /\bnegative\?\b/g, 
            /\bnewline\b/g, /\bnot\b/g, /\bnull-environment\b/g, /\bnull\?\b/g, /\bnumber-&gt;string\b/g, /\bnumber\?\b/g, 
            /\bnumerator\b/g, /\bodd\?\b/g, /\bopen-input-file\b/g, /\bopen-output-file\b/g, /\boutput-port\?\b/g, 
            /\bpair\?\b/g, /\bpeek-char\b/g, /\bport\?\b/g, /\bpositive\?\b/g, /\bprocedure\?\b/g, /\bquasiquote\b/g, 
            /\bquote\b/g, /\bquotient\b/g, /\brational\?\b/g, /\brationalize\b/g, /\bread\b/g, /\bread-char\b/g, 
            /\breal-part\b/g, /\breal\?\b/g, /\bremainder\b/g, /\breverse\b/g, /\bround\b/g, /\bscheme-report-environment\b/g, 
            /\bset!\b/g, /\bset-car!\b/g, /\bset-cdr!\b/g, /\bsin\b/g, /\bsqrt\b/g, /\bstring\b/g, /\bstring-&gt;list\b/g, 
            /\bstring-&gt;number\b/g, /\bstring-&gt;symbol\b/g, /\bstring-append\b/g, /\bstring-ci&lt;=\?\b/g, /\bstring-ci&lt;\?\b/g, 
            /\bstring-ci=\?\b/g, /\bstring-ci&gt;=\?\b/g, /\bstring-ci&gt;\?\b/g, /\bstring-copy\b/g, /\bstring-fill!\b/g, 
            /\bstring-length\b/g, /\bstring-ref\b/g, /\bstring-set!\b/g, /\bstring&lt;=\?\b/g, /\bstring&lt;\?\b/g, /\bstring=\?\b/g, 
            /\bstring&gt;=\?\b/g, /\bstring&gt;\?\b/g, /\bstring\?\b/g, /\bsubstring\b/g, /\bsymbol-&gt;string\b/g, /\bsymbol\?\b/g, 
            /\b#t\b/g, /\btan\b/g, /\btranscript-off\b/g, /\btranscript-on\b/g, /\btruncate\b/g, /\bvalues\b/g, /\bvector\b/g, 
            /\bvector-&gt;list\b/g, /\bvector-fill!\b/g, /\bvector-length\b/g, /\bvector-ref\b/g, /\bvector-set!\b/g, 
            /\bwith-input-from-file\b/g, /\bwith-output-to-file\b/g, /\bwrite\b/g, /\bwrite-char\b/g, /\bzero\?\b/g],
            "Word" : [/[a-zA-Z0-9_]+/g],
            "Symbol" : [/./g]
        },
        "Color" : {
            "Comment" : "darkgreen",
            "String" : "orange",
            "Keywords": "blue",
            "Integer" : "green",
            "Double" : "green",
            "Hex" : "green",
            "Octo" : "green"
        },
        "Multi" : {
            "Order": ["green", "blue", "magenta"],
            "Triggers": ["(", ")", "[", "]", "{", "}"]
        },
        "Indent" : {
            "Plus" : [],
            "Sign" : "\t",
            "Value" : 2
        }
    },
    "Refal": {
        "Regs" : {},
        "Color" : {},
        "Multi" : {
            "Order" : [],
            "Triggers" : []
        },
        "Indent" : {
            "Plus" : [],
            "Sign" : "",
            "Value" : 1
        }
    },
    "Markdown": {
        "Regs" : {
            "Text" : [/[\s\S]+/g],
            "Symbol" : [/./g]
        },
        "Color" : {},
        "Multi" : {
            "Order" : [],
            "Triggers" : []
        },
        "Indent" : {
            "Plus" : [],
            "Sign" : "",
            "Value" : 1
        }
    },
    "Plaintext": {
        "Regs" : {
            "Text" : [/[\s\S]+/g]
        },
        "Color" : {},
        "Multi" : {
            "Order" : [],
            "Triggers" : []
        },
        "Indent" : {
            "Plus" : [],
            "Sign" : "",
            "Value" : 1
        }
    }
}; 
