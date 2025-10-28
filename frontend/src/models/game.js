export class Player {
  constructor(id, name, isAdmin = false, score = 0) {
    this.id = id
    this.name = name
    this.isAdmin = isAdmin
    this.score = score
  }
}

export default class Game {
  constructor(id) {
    this.id = id
    this.players = []
  }

  addPlayer(player) {
    if (!this.players.find(p => p.id === player.id)) {
      this.players.push(player)
    }
  }

  removePlayer(id) {
    this.players = this.players.filter(p => p.id !== id)
  }
}
