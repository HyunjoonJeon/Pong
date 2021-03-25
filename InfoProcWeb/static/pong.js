// Global Variables
var DIRECTION = {
	IDLE: 0,
	UP: 1,
	DOWN: 2,
	LEFT: 3,
	RIGHT: 4
};

var rounds = [5, 5, 3, 3, 2];
var colors = ['#1abc9c', '#2ecc71', '#3498db', '#e74c3c', '#9b59b6'];

// The ball object (The cube that bounces back and forth)
var Ball = {
	new: function (incrementedSpeed) {
		return {
			width: 18,
			height: 18,
			x: (this.canvas.width / 2) - 9,
			y: (this.canvas.height / 2) - 9,
			moveX: DIRECTION.IDLE,
			moveY: DIRECTION.IDLE,
			speed: incrementedSpeed || 9
		};
	}
};

// The paddle object (The two lines that move up and down)
var Paddle = {
	new: function (side) {
		return {
			width: 18,
			height: 70,
			x: side === 'left' ? 150 : this.canvas.width - 150,
			y: (this.canvas.height / 2) - 35,
			score: 0,
			move: DIRECTION.IDLE,
			speed: 10
		};
	}
};

var Game = {
	initialize: function () {
		this.canvas = document.querySelector('canvas');
		this.context = this.canvas.getContext('2d');

		this.canvas.width = 1400;
		this.canvas.height = 1000;

		this.canvas.style.width = (this.canvas.width / 2) + 'px';
		this.canvas.style.height = (this.canvas.height / 2) + 'px';

		this.player1 = Paddle.new.call(this, 'left');
		this.player2 = Paddle.new.call(this, 'right');
		this.ball = Ball.new.call(this);

		this.player2.speed = 8;
		this.running = this.over = false;
		this.turn = this.player2;
		this.timer = this.round = 0;
		this.color = '#2c3e50';

	},

	endGameMenu: function (text) {
		// Change the canvas font size and color
		Pong.context.font = '50px Courier New';
		Pong.context.fillStyle = this.color;

		// Draw the rectangle behind the 'Press any key to begin' text.
		Pong.context.fillRect(
			Pong.canvas.width / 2 - 350,
			Pong.canvas.height / 2 - 48,
			700,
			100
		);

		// Change the canvas color;
		Pong.context.fillStyle = '#ffffff';

		// Draw the end game menu text ('Game Over' and 'Winner')
		Pong.context.fillText(text,
			Pong.canvas.width / 2,
			Pong.canvas.height / 2 + 15
		);

		setTimeout(function () {
			Pong = Object.assign({}, Game);
			Pong.initialize();
		}, 3000);
	},

	menu: function () {
		// Draw all the Pong objects in their current state
		Pong.draw();

		// Change the canvas font size and color
		this.context.font = '50px Courier New';
		this.context.fillStyle = this.color;

		// Draw the rectangle behind the 'Press any key to begin' text.
		this.context.fillRect(
			this.canvas.width / 2 - 350,
			this.canvas.height / 2 - 48,
			700,
			100
		);

		// Change the canvas color;
		this.context.fillStyle = '#ffffff';

		// Draw the 'press any key to begin' text
		this.context.fillText('Press any key to begin',
			this.canvas.width / 2,
			this.canvas.height / 2 + 15
		);
	},

	// Update all objects (move the player, paddle, ball, increment the score, etc.)
	update: function () {
		this.over = serverOver;
		if (!this.over) {
			this.player1.y = p1currentposy;
			this.player1.score = p1score;
			this.player2.y = p2currentposy;
			this.player2.score =p2score;
			this.ball.x    = ballposx;
			this.ball.y    = ballposy;
		}

			

		// Handle the end of round transition
		// Check to see if the player won the round.
		// if (this.player1.score === rounds[this.round]) {
		// 	// Check to see if there are any more rounds/levels left and display the victory screen if
		// 	// there are not.
		// 	if (!rounds[this.round + 1]) {
		// 		this.over = true;
		// 		setTimeout(function () { Pong.endGameMenu('Winner!'); }, 1000);
		// 	} else {
		// 		// If there is another round, reset all the values and increment the round number.
		// 		this.color = this._generateRoundColor();
		// 		this.player1.score = this.player2.score = 0;
		// 		this.player1.speed += 0.5;
		// 		this.player2.speed += 1;
		// 		this.ball.speed += 1;
		// 		this.round += 1;

		// 	}
		// }
		// // Check to see if the paddle/AI has won the round.
		// else if (this.player2.score === rounds[this.round]) {
		// 	this.over = true;
		// 	setTimeout(function () { Pong.endGameMenu('Game Over!'); }, 1000);
		// }
	},

	// Draw the objects to the canvas element
	draw: function () {
		// Clear the Canvas
		this.context.clearRect(
			0,
			0,
			this.canvas.width,
			this.canvas.height
		);

		// Set the fill style to black
		this.context.fillStyle = this.color;

		// Draw the background
		this.context.fillRect(
			0,
			0,
			this.canvas.width,
			this.canvas.height
		);

		// Set the fill style to white (For the paddles and the ball)
		this.context.fillStyle = '#ffffff';

		// Draw the Player
		this.context.fillRect(
			this.player1.x,
			this.player1.y,
			this.player1.width,
			this.player1.height
		);

		// Draw the Paddle
		this.context.fillRect(
			this.player2.x,
			this.player2.y,
			this.player2.width,
			this.player2.height
		);

		// Draw the Ball

		this.context.fillRect(
			this.ball.x,
			this.ball.y,
			this.ball.width,
			this.ball.height
		);


		// Draw the net (Line in the middle)
		this.context.beginPath();
		this.context.setLineDash([7, 15]);
		this.context.moveTo((this.canvas.width / 2), this.canvas.height - 140);
		this.context.lineTo((this.canvas.width / 2), 140);
		this.context.lineWidth = 10;
		this.context.strokeStyle = '#ffffff';
		this.context.stroke();

		// Set the default canvas font and align it to the center
		this.context.font = '100px Courier New';
		this.context.textAlign = 'center';

		// Draw the player1 score (left)
		this.context.fillText(
			this.player1.score.toString(),
			(this.canvas.width / 2) - 300,
			200
		);

		// Draw the player2 score (right)
		this.context.fillText(
			this.player2.score.toString(),
			(this.canvas.width / 2) + 300,
			200
		);

		// Change the font size for the center score text
		this.context.font = '30px Courier New';

		// Draw the winning score (center)
		this.context.fillText(
			'Round ' + (Pong.round + 1),
			(this.canvas.width / 2),
			35
		);

		// Change the font size for the center score value
		this.context.font = '40px Courier';

		// Draw the current round number
		this.context.fillText(
			rounds[Pong.round] ? rounds[Pong.round] : rounds[Pong.round - 1],
			(this.canvas.width / 2),
			100
		);
	},

	loop: function () {
		Pong.update();
		Pong.draw();

		// If the game is not over, draw the next frame.
		if (!Pong.over) requestAnimationFrame(Pong.loop);
	},

	// Select a random color as the background of each level/round.
	_generateRoundColor: function () {
		var newColor = colors[Math.floor(Math.random() * colors.length)];
		if (newColor === this.color) return Pong._generateRoundColor();
		return newColor;
	}
};

var Pong = Object.assign({}, Game);

Pong.initialize();
Pong.running = true;
window.requestAnimationFrame(Pong.loop);

