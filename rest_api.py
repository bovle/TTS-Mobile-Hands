from flask import Flask, request, render_template, redirect, url_for
import json

app = Flask(__name__, template_folder="templates")


cardsBuffer = {}
players = {}


@app.route('/')
def index():
    return render_template("index.html", name="frederik")


@app.route('/player/<player_id>')
def player(player_id):
    player_id = int(player_id)
    cards = []
    if player_id in players.keys():
        for card in players[player_id]:
            deckID = int(card['CardID'] / 100)
            cardID = int(card['CardID'] % 100)
            num_cols = card['CustomDeck'][str(deckID)]['NumWidth']
            row = int(cardID/num_cols)
            column = int(cardID % num_cols)
            decals = []
            if 'AttachedDecals' in card:
                for decal in card['AttachedDecals']:
                    d = {
                        'url': decal['CustomDecal']['ImageURL'],
                        'top': (((decal['Transform']['posZ'] / 1.5) * 39) + 40) - 2.25,
                        'left': ((decal['Transform']['posX'] * -44) + 45) - 2.25
                    }
                    decals.append(d)
            cards.append({
                'url': card['CustomDeck'][str(deckID)]['FaceURL'],
                'CardID': card['CardID'],
                'num_rows': card['CustomDeck'][str(deckID)]['NumHeight'],
                'num_cols': num_cols,
                'row': row,
                'col': column,
                'decals': decals
            })
    return render_template("player.html", cards=cards)


@app.route('/update')
def update():
    if len(cardsBuffer) == 0:
        return "none"
    else:
        res = json.dumps(cardsBuffer)
        cardsBuffer.clear()
        return res


@app.route('/sendcard/<player_id>', methods=['PUT', 'POST'])
def sendCard(player_id):

    # from tabletop
    if request.method == 'PUT':
        player_id = int(player_id)
        cardData = json.loads(request.data)
        cardData['Transform']['rotZ'] = 0
        print("sending card to player " + str(player_id))
        if player_id not in players.keys():
            players[player_id] = []
        players[player_id].append(cardData)
        return "card sent"
    # from web
    if request.method == 'POST':
        player_id = int(request.referrer.split('/')[-1])
        cardID = request.form['CardID']
        playerCards = players[player_id]
        for card in playerCards:
            if card['CardID'] == int(cardID):
                card['Transform']['rotZ'] = 180
                if not player_id in cardsBuffer:
                    cardsBuffer[player_id] = {}
                cardsBuffer[player_id][len(cardsBuffer[player_id])] = card
                players[player_id].remove(card)

        return redirect(url_for('player', player_id=player_id), code=303)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
