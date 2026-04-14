/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import {
    DEFAULT_GRID_SIZE,
    advanceState,
    createInitialState,
    queueDirection,
    toCellKey,
} from "@i_tech_royal_rahmani_base/js/snake_game_logic";

const KEYBOARD_DIRECTIONS = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right",
    w: "up",
    W: "up",
    a: "left",
    A: "left",
    s: "down",
    S: "down",
    d: "right",
    D: "right",
};

export class SnakeGameAction extends Component {
    static template = "i_tech_royal_rahmani_base.SnakeGameAction";

    setup() {
        this.intervalId = null;
        this.state = useState(createInitialState());
        this.handleKeydown = this.handleKeydown.bind(this);

        onMounted(() => {
            window.addEventListener("keydown", this.handleKeydown);
            this.startTicker();
        });

        onWillUnmount(() => {
            window.removeEventListener("keydown", this.handleKeydown);
            this.stopTicker();
        });
    }

    get cells() {
        const snakeCells = new Set(this.state.snake.map(toCellKey));
        const foodCell = this.state.food ? toCellKey(this.state.food) : null;
        const cells = [];

        for (let y = 0; y < this.state.gridSize; y++) {
            for (let x = 0; x < this.state.gridSize; x++) {
                const key = `${x},${y}`;
                let kind = "empty";
                if (foodCell === key) {
                    kind = "food";
                } else if (snakeCells.has(key)) {
                    kind = key === toCellKey(this.state.snake[0]) ? "head" : "snake";
                }

                cells.push({
                    key,
                    kind,
                });
            }
        }

        return cells;
    }

    get gridStyle() {
        return `grid-template-columns: repeat(${this.state.gridSize}, 1fr);`;
    }

    get statusLabel() {
        if (this.state.status === "paused") {
            return "Paused";
        }
        if (this.state.status === "gameover") {
            return "Game over";
        }
        if (this.state.status === "won") {
            return "Board cleared";
        }
        return "Running";
    }

    startTicker() {
        this.stopTicker();
        this.intervalId = window.setInterval(() => {
            if (this.state.status !== "running") {
                return;
            }
            this.patchState(advanceState(this.state));
        }, this.state.tickMs);
    }

    stopTicker() {
        if (this.intervalId) {
            window.clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    patchState(nextState) {
        Object.assign(this.state, nextState);
    }

    setDirection(direction) {
        this.patchState(queueDirection(this.state, direction));
    }

    goUp() {
        this.setDirection("up");
    }

    goLeft() {
        this.setDirection("left");
    }

    goDown() {
        this.setDirection("down");
    }

    goRight() {
        this.setDirection("right");
    }

    handleKeydown(event) {
        const target = event.target;
        const isTyping =
            target &&
            (target.tagName === "INPUT" ||
                target.tagName === "TEXTAREA" ||
                target.isContentEditable);
        if (isTyping) {
            return;
        }

        const direction = KEYBOARD_DIRECTIONS[event.key];
        if (direction) {
            event.preventDefault();
            this.setDirection(direction);
            return;
        }

        if (event.key === " " || event.key === "Spacebar" || event.key === "p" || event.key === "P") {
            event.preventDefault();
            this.togglePause();
            return;
        }

        if (event.key === "Enter" && (this.state.status === "gameover" || this.state.status === "won")) {
            event.preventDefault();
            this.restart();
        }
    }

    togglePause() {
        if (this.state.status === "gameover" || this.state.status === "won") {
            return;
        }
        this.state.status = this.state.status === "paused" ? "running" : "paused";
    }

    restart() {
        this.patchState(
            createInitialState({
                gridSize: this.state.gridSize || DEFAULT_GRID_SIZE,
                tickMs: this.state.tickMs,
            })
        );
    }
}

registry.category("actions").add("i_tech_royal_rahmani_base.snake_game", SnakeGameAction);
