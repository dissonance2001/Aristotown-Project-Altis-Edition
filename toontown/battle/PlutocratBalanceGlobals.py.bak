from toontown.battle import SuitBattleGlobals


def _attack(name, hp, acc, freq):
    return SuitBattleGlobals.SuitAttack(name, hp=(hp,), acc=(acc,), freq=(freq,))


def apply():
    attrs = SuitBattleGlobals.SuitAttributes

    attrs['charon']['hp'] = (2000,)
    attrs['charon']['def'] = (70,)
    attrs['charon']['attacks'] = (
        _attack('Demotion', 36, 90, 30),
        _attack('RedTape', 34, 85, 20),
        _attack('PeckingOrder', 36, 90, 25),
        _attack('PowerTrip', 32, 85, 25),
    )

    attrs['nix']['hp'] = (1675,)
    attrs['nix']['def'] = (80,)
    attrs['nix']['attacks'] = (
        _attack('PlayHardball', 33, 90, 30),
        _attack('RubOut', 29, 85, 15),
        _attack('Canned', 31, 90, 25),
        _attack('PowerTrip', 26, 85, 30),
    )

    attrs['hydra']['hp'] = (1800,)
    attrs['hydra']['def'] = (80,)
    attrs['hydra']['attacks'] = (
        _attack('Chomp', 31, 90, 30),
        _attack('Bite', 27, 85, 25),
        _attack('Crunch', 30, 90, 25),
        _attack('Synergy', 26, 85, 25),
    )

    attrs['styx']['hp'] = (1625,)
    attrs['styx']['def'] = (80,)
    attrs['styx']['attacks'] = (
        _attack('Watercooler', 34, 90, 30),
        _attack('Liquidate', 32, 85, 20),
        _attack('FreezeAssets', 33, 90, 30),
        _attack('Synergy', 30, 85, 20),
    )

    attrs['kerberos']['hp'] = (1850,)
    attrs['kerberos']['def'] = (75,)
    attrs['kerberos']['attacks'] = (
        _attack('Withdrawal', 32, 90, 30),
        _attack('BounceCheck', 28, 85, 30),
        _attack('PickPocket', 31, 90, 25),
        _attack('Synergy', 27, 85, 15),
    )

    attrs['pcrat']['hp'] = (6000,)
    attrs['pcrat']['def'] = (70,)
    attrs['pcrat']['attacks'] = (
        _attack('PickPocket', 31, 80, 15),
        _attack('Synergy', 29, 95, 20),
        _attack('MarketCrash', 34, 90, 20),
        _attack('CigarSmoke', 37, 75, 15),
        _attack('FreezeAssets', 36, 95, 30),
    )


apply()
