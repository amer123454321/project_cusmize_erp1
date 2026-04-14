/** @odoo-module **/

export const DEFAULT_GRID_SIZE = 16;
export const DEFAULT_TICK_MS = 180;

export const DIRECTIONS = {
    up: { x: 0, y: -1 },
    down: { x: 0, y: 1 },
    left: { x: -1, y: 0 },
    right: { x: 1, y: 0 },
};

const OPPOSITE_DIRECTIONS = {
    up: "down",
    down: "up",
    left: "right",
    right: "left",
};

export function toCellKey(position) {
    return `${position.x},${position.y}`;
}

export function getAvailableCells(snake, gridSize) {
    const occupiedCells = new Set(snake.map(toCellKey));
    const availableCells = [];

    for (let y = 0; y < gridSize; y++) {
        for (let x = 0; x < gridSize; x++) {
            const position = { x, y };
            if (!occupiedCells.has(toCellKey(position))) {
                availableCells.push(position);
            }
        }
    }

    return availableCells;
}

export function createFoodPosition(snake, gridSize, randomFn = Math.random) {
    const availableCells = getAvailableCells(snake, gridSize);
    if (!availableCells.length) {
        return null;
    }

    const randomIndex = Math.floor(randomFn() * availableCells.length);
    return availableCells[randomIndex];
}

export function createInitialState(options = {}) {
    const gridSize = options.gridSize || DEFAULT_GRID_SIZE;
    const randomFn = options.randomFn || Math.random;
    const startX = Math.max(2, Math.floor(gridSize / 2));
    const startY = Math.floor(gridSize / 2);
    const snake = [
        { x: startX, y: startY },
        { x: startX - 1, y: startY },
        { x: startX - 2, y: startY },
    ];

    return {
        gridSize,
        tickMs: options.tickMs || DEFAULT_TICK_MS,
        snake,
        direction: "right",
        pendingDirection: "right",
        food: createFoodPosition(snake, gridSize, randomFn),
        score: 0,
        status: "running",
    };
}

export function queueDirection(state, nextDirection) {
    if (!DIRECTIONS[nextDirection]) {
        return state;
    }

    const referenceDirection = state.pendingDirection || state.direction;
    if (state.snake.length > 1 && OPPOSITE_DIRECTIONS[referenceDirection] === nextDirection) {
        return state;
    }

    return {
        ...state,
        pendingDirection: nextDirection,
    };
}

export function advanceState(state, randomFn = Math.random) {
    if (state.status !== "running") {
        return state;
    }

    const nextDirection = state.pendingDirection || state.direction;
    const movement = DIRECTIONS[nextDirection];
    const currentHead = state.snake[0];
    const nextHead = {
        x: currentHead.x + movement.x,
        y: currentHead.y + movement.y,
    };

    const hitBoundary =
        nextHead.x < 0 ||
        nextHead.y < 0 ||
        nextHead.x >= state.gridSize ||
        nextHead.y >= state.gridSize;
    if (hitBoundary) {
        return {
            ...state,
            direction: nextDirection,
            pendingDirection: nextDirection,
            status: "gameover",
        };
    }

    const willEatFood = state.food && nextHead.x === state.food.x && nextHead.y === state.food.y;
    const snakeBody = willEatFood ? state.snake : state.snake.slice(0, -1);
    const hitSelf = snakeBody.some((segment) => segment.x === nextHead.x && segment.y === nextHead.y);
    if (hitSelf) {
        return {
            ...state,
            direction: nextDirection,
            pendingDirection: nextDirection,
            status: "gameover",
        };
    }

    const nextSnake = [nextHead, ...snakeBody];
    const nextFood = willEatFood
        ? createFoodPosition(nextSnake, state.gridSize, randomFn)
        : state.food;

    return {
        ...state,
        snake: nextSnake,
        direction: nextDirection,
        pendingDirection: nextDirection,
        food: nextFood,
        score: state.score + (willEatFood ? 1 : 0),
        status: nextFood ? "running" : "won",
    };
}
