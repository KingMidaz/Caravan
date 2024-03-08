import json
import cards

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, cards.Card): 
            return { "suit": obj.suit.value, "num": obj.num.value, "idx": obj.idx }
        if isinstance(obj, cards.Hand): 
            a = []
            for c in obj.cards:
                a.append({"suit": c.suit.value, "num": c.num.value, "idx": c.idx})
            return {"hand": a}
        if isinstance(obj, cards.Lane):
            a = []
            for c in obj.cards:
                a.append({"suit": c.suit.value, "num": c.num.value, "idx": c.idx})
            return { "lane": a }
        return json.JSONEncoder.default(self, obj)