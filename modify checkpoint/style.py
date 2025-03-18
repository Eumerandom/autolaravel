style = """
    <style>
        * {
            font-family:'Poppins' !important;
        }
        [data-testid="stHeader"] {
            height: 70px !important;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 0px 0px 40px;
            border-top: none;
        }
        [data-testid="stHeader"]::before {
            content: "";
            background: url('https://laravel.com/img/logomark.min.svg') no-repeat center;
            background-size: contain;
            width: 50px;
            height: 50px;
            padding: 20px !important;
            display: block;
        }
        .stMainBlockContainer {
            width: 60vw !important;
            margin: auto !important;
            margin-top: 0 !important;
            padding-top: 40px !important;
            padding-bottom: 0 !important;
            text-align: center !important;
        }
        .stButton>button {
            background-color: #ff2d20 !important;
            color: white !important;
            font-size: 16px !important;
            width: 150px !important;
            padding: 10px !important;
            border-radius: 8px !important;
            margin: auto !important;
        }
        .stButton>button:hover {
            background-color: #171717 !important;
            color: #ff2d20 !important;
            border: 1px solid #ff2d20 !important;
        }
        .stTextInput>div>div>input {
            text-align: left !important;
            font-size: 14px !important;
            padding: 10px !important;
        }
        .stTextInput .stColumns {
            width: 30vw !important;
            justify-content: center !important;
            margin: auto !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            justify-content: center !important;
            margin: auto !important;
        }
        .stTabs [data-baseweb="tab"] {
            flex-grow: 0.5 !important;
            text-align: center !important;
            font-size: 20px !important;
            font-weight: bold !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            border-bottom: 1px solid #ff2d20 !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            width: 40vw !important;
            justify-content: center !important;
            margin: auto !important;
        }
        .stHeader {
            margin-bottom: 40px !important;
        }
        /*
        .stText .stMarkdown {
            justify-content: center !important;
            margin: auto !important;
        }
        */
    </style>
    """