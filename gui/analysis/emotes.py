import glob
import requests


emotes_channels = [
    'las',
    'guit',
    'valera',
    'roflan',
    'etm',
    'etz',
    'cake',
    'lirik',
    'forsen',
    'mob',
    'nuke',
    'wlg',
    'segall'
]

def get_bttv_local(channel):
    files = glob.glob("emotes_channels\\*.txt")
    if "emotes_channels\\{}.txt".format(channel+'_bttv') in files:
        with open("emotes_channels\\{}.txt".format(channel+'_bttv'), encoding="utf8") as f:
            data = [d.strip() for d in f.readlines()]
        return data

    emotes = requests.get("https://api.betterttv.net/2/channels/" + channel).json()
    if not 'emotes' in emotes:
        codes = []
    else:
        codes = [emote['code'] for emote in emotes['emotes']]

    with open("emotes_channels\\{}.txt".format(channel+'_bttv'), 'w+', encoding="utf8") as f:
        for code in codes:
            f.write(code+'\n')

    return codes


def get_ffz_local(channel):
    files = glob.glob("emotes_channels\\*.txt")
    if "emotes_channels\\{}.txt".format(channel+'_ffz') in files:
        with open("emotes_channels\\{}.txt".format(channel+'_ffz'), encoding="utf8") as f:
            data = [d.strip() for d in f.readlines()]
        return data

    emotes = requests.get("https://api.frankerfacez.com/v1/room/" + channel).json()
    if not 'sets' in emotes or len(emotes['sets'][str(list(emotes['sets'].keys())[0])]['emoticons']) == 0:
        codes = []
    else:
        emotes_data = emotes['sets'][str(list(emotes['sets'].keys())[0])]['emoticons']
        codes = [emote['name'] for emote in emotes_data]

    with open("emotes_channels\\{}.txt".format(channel+'_ffz'), 'w+', encoding="utf8") as f:
        for code in codes:
            f.write(code+'\n')

    return codes

emotes_bttv_global = ["OhMyGoodness", "PancakeMix", "PedoBear", "PokerFace", "RageFace", "RebeccaBlack", ":tf:", "aPliS", "CiGrip", "CHAccepted", "FuckYea", "DatSauce", "ForeverAlone", "GabeN", "HailHelix", "HerbPerve", "iDog", "rStrike", "ShoopDaWhoop", "SwedSwag", "M&Mjc", "bttvNice", "TopHam", "TwaT", "WhatAYolk", "WatChuSay", "Blackappa", "DogeWitIt", "BadAss", "SavageJerky", "Zappa", "tehPoleCat", "AngelThump", "Kaged", "HHydro", "TaxiBro", "BroBalt", "ButterSauce", "BaconEffect", "SuchFraud", "CandianRage", "She'llBeRight", "OhhhKee", "D:", "SexPanda", "(poolparty)", ":'(", "(puke)", "bttvWink", "bttvAngry", "bttvConfused", "bttvCool", "bttvHappy", "bttvSad", "bttvSleep", "bttvSurprised", "bttvTongue", "bttvUnsure", "bttvGrin", "bttvHeart", "bttvTwink", "VisLaud", "(chompy)", "SoSerious", "BatKappa", "KaRappa", "YetiZ", "miniJulia", "FishMoley", "Hhhehehe", "KKona", "OhGod", "PoleDoge", "motnahP", "sosGame", "CruW", "RarePepe", "iamsocal", "haHAA", "FeelsBirthdayMan", "RonSmug", "KappaCool", "FeelsBadMan", "BasedGod", "bUrself", "ConcernDoge", "FapFapFap", "FeelsGoodMan", "FireSpeed", "NaM", "SourPls", "LuL", "SaltyCorn", "FCreep", "VapeNation", "ariW", "notsquishY", "FeelsAmazingMan", "DuckerZ", "SqShy", "Wowee"]

emotes_global = [
    "JKanStyle",
    "OptimizePrime",
    "StoneLightning",
    "TheRinger",
    "RedCoat",
    "Kappa",
    "JonCarnage",
    "MrDestructoid",
    "BCWarrior",
    "GingerPower",
    "DansGame",
    "SwiftRage",
    "PJSalt",
    "KevinTurtle",
    "Kreygasm",
    "SSSsss",
    "PunchTrees",
    "FunRun",
    "ArsonNoSexy",
    "SMOrc",
    "FrankerZ",
    "OneHand",
    "HassanChop",
    "BloodTrail",
    "DBstyle",
    "AsianGlow",
    "BibleThump",
    "ShazBotstix",
    "PogChamp",
    "PMSTwin",
    "FUNgineer",
    "ResidentSleeper",
    "4Head",
    "HotPokket",
    "FailFish",
    "DAESuppy",
    "WholeWheat",
    "ThunBeast",
    "TF2John",
    "RalpherZ",
    "Kippa",
    "Keepo",
    "BigBrother",
    "SoBayed",
    "PeoplesChamp",
    "GrammarKing",
    "PanicVis",
    "ANELE",
    "BrokeBack",
    "PipeHype",
    "YouWHY",
    "RitzMitz",
    "EleGiggle",
    "TheThing",
    "HassaanChop",
    "BabyRage",
    "panicBasket",
    "PermaSmug",
    "BuddhaBar",
    "WutFace",
    "PRChase",
    "Mau5",
    "HeyGuys",
    "NotATK",
    "mcaT",
    "TTours",
    "PraiseIt",
    "HumbleLife",
    "CorgiDerp",
    "ArgieB8",
    "ShadyLulu",
    "KappaPride",
    "CoolCat",
    "DendiFace",
    "NotLikeThis",
    "riPepperonis",
    "duDudu",
    "bleedPurple",
    "twitchRaid",
    "SeemsGood",
    "MingLee",
    "KappaRoss",
    "KappaClaus",
    "OhMyDog",
    "OPFrog",
    "SeriousSloth",
    "KomodoHype",
    "VoHiYo",
    "MikeHogu",
    "KappaWealth",
    "cmonBruh",
    "SmoocherZ",
    "NomNom",
    "StinkyCheese",
    "ChefFrank",
    "FutureMan",
    "OpieOP",
    "DoritosChip",
    "PJSugar",
    "VoteYea",
    "VoteNay",
    "RuleFive",
    "DxCat",
    "DrinkPurple",
    "TinyFace",
    "PicoMause",
    "TheTarFu",
    "DatSheffy",
    "UnSane",
    "copyThis",
    "pastaThat",
    "imGlitch",
    "GivePLZ",
    "TakeNRG",
    "BlargNaut",
    "DogFace",
    "Jebaited",
    "TooSpicy",
    "WTRuck",
    "UncleNox",
    "RaccAttack",
    "StrawBeary",
    "PrimeMe",
    "BrainSlug",
    "BatChest",
    "CurseLit",
    "Poooound",
    "FreakinStinkin",
    "SuperVinlin",
    "TriHard",
    "CoolStoryBob",
    "ItsBoshyTime",
    "KAPOW",
    "YouDontSay",
    "UWot",
    "RlyTho",
    "SoonerLater",
    "PartyTime",
    "NinjaGrumpy",
    "MVGame",
    "TBAngel",
    "TheIlluminati",
    "BlessRNG",
    "MorphinTime",
    "ThankEgg",
    "ArigatoNas",
    "BegWan",
    "BigPhish",
    "InuyoFace",
    "Kappu",
    "KonCha",
    "PunOko",
    "SabaPing",
    "TearGlove",
    "TehePelo",
    "TwitchLit",
    "CarlSmile",
    "CrreamAwk",
    "TwitchRPG",
    "Squid1",
    "Squid2",
    "Squid3",
    "Squid4",
    "TwitchUnity",
    "TPcrunchyroll",
    "EntropyWins",
    "LUL",
    "PowerUpR",
    "PowerUpL",
    "HSCheers",
    "HSWP",
    "DarkMode",
    "TwitchVotes",
    "TPFufun",
    "RedTeam",
    "GreenTeam",
    "HappyJack",
    "AngryJack",
    "PurpleStar",
    "FBtouchdown",
    "PopCorn",
    "r6rekt",
    "r6deal",
    "r6salute",
    "SC20zerg",
    "SC20protoss",
    "SC20terran",
    "SnickersHype",
    "SOTshark",
    "SOTahoy",
    "BestPi",
    "WorstPi",
    "EatPi",
    "TombRaid"
]