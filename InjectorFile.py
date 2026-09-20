from toontown.clashbattle.battle import BattleGUI as G

for pos, t in enumerate(base.localAvatar.inventory.getGagOrder()):
    v = int(t)
    print(pos, t.name, 'value', v,
          '| Tracks:', G.Tracks[v],
          '| color:', tuple(round(c, 2) for c in G.TrackColors[v]),
          '| first gag:', G.AvPropsNew[v][0])