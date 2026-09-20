# Suit Shortnames (for CSEditorUtil.makeSuits)

Reference list of valid `name` strings for `CSEditorUtil.makeSuits(...)` in the cutscene editor.
Source: `toontown/suit/SuitDefinitions.py`.

## SELLBOT

| Shortname | Cog |
|---|---|
| cc | Cold Caller |
| tm | Telemarketer |
| nd | Name Dropper |
| gh | Glad Hander |
| ms | Mover & Shaker |
| tf | Two-Face |
| mi | Mingler |
| mh | Mr. Hollywood |
| foreman | Factory Foreman (miniboss) |
| dopr | D.O.P.R. (miniboss) |
| dopa | D.O.P.A. (miniboss) |
| bellring | Bellringer (merc miniboss) |
| prethink | Prethinker (merc miniboss) |
| mslacker | Multislacker (merc miniboss) |
| msfore | Multislacker Foreman (miniboss) |
| psetter | Pacesetter (merc miniboss) |

## CASHBOT

| Shortname | Cog |
|---|---|
| sc | Short Change |
| pp | Penny Pincher |
| tw | Tightwad |
| bc | Bean Counter |
| nc | Number Cruncher |
| mb | Money Bags |
| ls | Loan Shark |
| rb | Robber Baron |
| supervis | Mint Supervisor (miniboss) |
| erfit | Count Erfit (miniboss) |
| duckshfl | Duck Shuffler (merc miniboss) |
| treek | Treekiller (merc miniboss) |
| pcrat | Plutocrat (merc miniboss) |
| charon | Charon (merc miniboss) |
| nix | Nix (merc miniboss) |
| hydra | Hydra (merc miniboss) |
| styx | Styx (merc miniboss) |
| kerberos | Kerberos (merc miniboss) |
| hroller | High Roller (merc miniboss) |
| hrollerc | High Roller Clone (miniboss) |

## LAWBOT

| Shortname | Cog |
|---|---|
| bf | Bottom Feeder |
| b | Bloodsucker |
| btto | TTO Bloodsucker |
| pf | Pettifogger |
| dt | Double Talker |
| nn | Needlenose (female) |
| ac | Ambulance Chaser |
| cv | Conveyancer |
| bs | Backstabber |
| ad | Advocate |
| sd | Spin Doctor |
| sh | Shyster (female) |
| le | Legal Eagle |
| br | Barrister |
| bw | Big Wig |
| clerk | Head Attorney (miniboss) |
| count | Count Erclaim (miniboss) |
| redd | Redd (miniboss) |
| judy | Judy (unique, female) |
| lgator | Litigator (miniboss) |
| stenog | Stenographer (miniboss, female) |
| caseman | Case Manager (miniboss) |
| sgoat | Scapegoat (miniboss) |
| mouthp | Mouthpiece (merc miniboss) |
| rainmake | Rainmaker (merc miniboss, female) |
| whunter | Witch Hunter (merc miniboss) |

## BOSSBOT

| Shortname | Cog |
|---|---|
| f | Flunky |
| p | Pencil Pusher |
| ym | Yesman |
| mm | Micromanager |
| ds | Downsizer |
| hh | Head Hunter |
| cr | Corporate Raider |
| tbc | The Big Cheese |
| clubpres | Club President (miniboss) |
| autocad | Autocaddie (unique) |
| djockey | Desk Jockey (unique, hidden dept) |
| derrman | Derrick Man (miniboss) |
| derrhand | Derrick Hand (miniboss) |
| ptjockey | Prethinker Jockey (unique, dept override "Brianbot") |
| fires | Firestarter (merc miniboss) |
| fbed | Featherbedder (merc miniboss) |
| mplayer | Major Player (merc miniboss) |
| chainsaw | Chainsaw Consultant (merc miniboss) |

## BOARDBOT

| Shortname | Cog |
|---|---|
| bgh | Bag Holder |
| pph | Paper Hands |
| ins | Insider |
| cbr | Circuit Breaker |
| dl | Dead Lock |
| shw | Shark Watcher |
| mg | Magnate |
| hho | Head Honcho |
| chairman | Chairman (unique) |
| ottoman | Ottoman (unique) |
| dlao | D.L.A.O. (miniboss) |
| dold | D.O.L.D. (miniboss) |
| ddiver | Deep Diver (merc miniboss) |
| gatekeep | Gatekeeper (merc miniboss) |

## Misc

| Shortname | Cog |
|---|---|
| test | Test Cog (hidden department, BOARDBOT internally) |

## Not usable

- `standin` — "Witness Standin" LAWBOT miniboss. Its `SuitDefinition` in `SuitDefinitions.py` is still commented out, so `newSuit('standin')` will fail.
