from runefumbler.fumbler import build_trade_opps, fumble_opp


def testBuildTradeOps():
    test_string = "Swordfish : 178 : 183 : 100 : Gold amulet (u) : 122 : 137 : 100 : Swamp paste : 5 : 10 : 100 : Steam rune : 110 : 116 : 13 : Lava rune : 20 : 25 : 90 : Amethyst dart : 237 : 244 : 46 : Lantern lens : 13 : 18 : 125 : Dragon javelin : 883 : 907 : 117 :"
    ops = build_trade_opps(test_string)
    assert len(ops) == 8
    assert (
        ops[0].to_json()
        == '{"name": "Swordfish", "buy": "178", "sell": "183", "time": "100"}'
    )
