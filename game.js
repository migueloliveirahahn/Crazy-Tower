const config = {
    type: Phaser.AUTO,
    width: 400,
    height: 600,
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 1000 },
            debug: false
        }
    },
    scene: {
        preload,
        create,
        update
    }
};

let game = new Phaser.Game(config);

let player, platforms, cursors, spaceKey;
let score = 0;
let scoreText, highScoreText;
let maxY = 0;
let gameOver = false;
let restartButton;
let highScore = 0;
let nextPlatformY = 400;

// Variáveis para imagens e texto de game over
let gameOverImage, recordText;

function preload() {
    this.load.image('background', 'assets/fundo.jpeg');
    this.load.image('platform', 'assets/Plataforma.jpeg');
    this.load.image('player', 'assets/idle.gif');
    // Carregue a imagem Restart.png como botão
    this.load.image('restartButton', 'assets/Restart.png');
}

function create() {
    highScore = localStorage.getItem('crazyTowerHighScore') || 0;

    this.add.tileSprite(0, 0, 800, 6000, 'background').setOrigin(0).setScrollFactor(0);

    platforms = this.physics.add.staticGroup();
    platforms.create(200, 550, 'platform').setOrigin(0.5).refreshBody();

    player = this.physics.add.sprite(200, 500, 'player').setScale(1);
    player.setCollideWorldBounds(false);
    player.setBounce(0);
    player.setSize(12, 28);
    player.setOffset(10, 5);

    let lastY = 550;
    for (let i = 0; i < 8; i++) {
        const spacing = Phaser.Math.Between(55, 75);
        let x;
        let y = lastY - spacing;

        let tries = 0;
        const maxTries = 10;
        let validPosition = false;

        while (!validPosition && tries < maxTries) {
            x = Phaser.Math.Between(50, 300);

            validPosition = true;
            platforms.getChildren().forEach((plat) => {
                const dx = Math.abs(plat.x - x);
                const dy = Math.abs(plat.y - y);

                if (dx < 70 && dy < 40) {
                    validPosition = false;
                }
            });

            tries++;
        }

        platforms.create(x, y, 'platform').setOrigin(0.5).refreshBody();
        lastY = y;
    }
    nextPlatformY = lastY;

    this.physics.add.collider(player, platforms);

    cursors = this.input.keyboard.createCursorKeys();
    spaceKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

    this.cameras.main.startFollow(player);
    this.cameras.main.setBounds(0, -6000, 400, 6600);

    scoreText = this.add.text(10, 10, 'Pontuação: 0', {
        font: '20px Consolas',
        fill: '#ffffff'
    }).setScrollFactor(0);

    highScoreText = this.add.text(10, 40, `Recorde: ${highScore}`, {
        font: '20px Consolas',
        fill: '#ffcc00'
    }).setScrollFactor(0);

    restartButton = this.add.image(200, 340, 'restartButton')
        .setInteractive()
        .setVisible(false)
        .setScrollFactor(0)
        .setScale(0.3)  // ajuste o tamanho para ficar bom
        .setDepth(999);

    restartButton.on('pointerdown', () => {
        this.scene.restart();
        resetGameState();
    });

    this.input.keyboard.on('keydown-R', () => {
        if (gameOver) {
            this.scene.restart();
            resetGameState();
        }
    });

    // Removi o gameOverImage, usando só o botão como feedback visual

    recordText = this.add.text(200, 230, '🏆 Recorde!', {
        font: '26px Consolas',
        fill: '#ffffff'
    })
        .setOrigin(0.5)
        .setScrollFactor(0)
        .setDepth(999)
        .setVisible(false);

    maxY = player.y;
}

function update() {
    if (gameOver) return;

    if (cursors.left.isDown) {
        player.setVelocityX(-200);
    } else if (cursors.right.isDown) {
        player.setVelocityX(200);
    } else {
        player.setVelocityX(0);
    }

    if ((cursors.up.isDown || spaceKey.isDown) && player.body.blocked.down) {
        player.setVelocityY(-525);
    }

    const bottomLimit = this.cameras.main.scrollY + 600;
    if (player.y > bottomLimit) {
        triggerGameOver(this);
    }

    if (player.y < maxY - 20) {
        const diff = Math.floor((maxY - player.y) / 20);
        score += diff;
        maxY = player.y;
        scoreText.setText('Pontuação: ' + score);
    }

    const camTop = this.cameras.main.scrollY - 100;

    while (nextPlatformY > camTop) {
        const spacing = Phaser.Math.Between(55, 75);
        let x;
        let y = nextPlatformY - spacing;

        let tries = 0;
        const maxTries = 10;
        let validPosition = false;

        while (!validPosition && tries < maxTries) {
            x = Phaser.Math.Between(50, 300);

            validPosition = true;
            platforms.getChildren().forEach((plat) => {
                const dx = Math.abs(plat.x - x);
                const dy = Math.abs(plat.y - y);

                if (dx < 70 && dy < 40) {
                    validPosition = false;
                }
            });

            tries++;
        }

        platforms.create(x, y, 'platform').setOrigin(0.5).refreshBody();
        nextPlatformY = y;
    }

    platforms.getChildren().forEach((plat) => {
        if (plat.y > this.cameras.main.scrollY + 700) plat.destroy();
    });
}

function resetGameState() {
    score = 0;
    maxY = 0;
    gameOver = false;

    restartButton.setVisible(false);
    recordText.setVisible(false);
}

function triggerGameOver(scene) {
    if (gameOver) return;

    gameOver = true;
    player.setVelocity(0, 0);
    player.body.enable = false;

    restartButton.setVisible(true);

    if (score > highScore) {
        highScore = score;
        localStorage.setItem('crazyTowerHighScore', highScore);
        highScoreText.setText(`Recorde: ${highScore}`);
        recordText.setVisible(true);
    }
}
