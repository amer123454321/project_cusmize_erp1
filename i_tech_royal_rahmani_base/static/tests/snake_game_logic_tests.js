/** @odoo-module **/

import {
    advanceState,
    createFoodPosition,
    createInitialState,
    queueDirection,
} from "@i_tech_royal_rahmani_base/js/snake_game_logic";

QUnit.module("i_tech_royal_rahmani_base > snake_game_logic");

QUnit.test("snake advances one cell in its current direction", function (assert) {
    const state = createInitialState({ gridSize: 10 });
    const nextState = advanceState(state, () => 0);

    assert.deepEqual(nextState.snake[0], { x: state.snake[0].x + 1, y: state.snake[0].y });
    assert.strictEqual(nextState.snake.length, state.snake.length);
    assert.strictEqual(nextState.status, "running");
});

QUnit.test("queued opposite direction is ignored", function (assert) {
    const state = createInitialState({ gridSize: 10 });
    const nextState = queueDirection(state, "left");

    assert.strictEqual(nextState.pendingDirection, "right");
});

QUnit.test("eating food grows the snake and increments score", function (assert) {
    const state = {
        ...createInitialState({ gridSize: 8 }),
        snake: [
            { x: 3, y: 3 },
            { x: 2, y: 3 },
            { x: 1, y: 3 },
        ],
        direction: "right",
        pendingDirection: "right",
        food: { x: 4, y: 3 },
    };

    const nextState = advanceState(state, () => 0);

    assert.strictEqual(nextState.score, 1);
    assert.strictEqual(nextState.snake.length, 4);
    assert.deepEqual(nextState.snake[0], { x: 4, y: 3 });
    assert.notDeepEqual(nextState.food, { x: 4, y: 3 });
});

QUnit.test("wall collisions end the game", function (assert) {
    const state = {
        ...createInitialState({ gridSize: 4 }),
        snake: [
            { x: 3, y: 2 },
            { x: 2, y: 2 },
            { x: 1, y: 2 },
        ],
        direction: "right",
        pendingDirection: "right",
    };

    const nextState = advanceState(state, () => 0);

    assert.strictEqual(nextState.status, "gameover");
});

QUnit.test("food placement skips occupied snake cells", function (assert) {
    const snake = [
        { x: 0, y: 0 },
        { x: 1, y: 0 },
        { x: 2, y: 0 },
    ];

    const food = createFoodPosition(snake, 3, () => 0);

    assert.deepEqual(food, { x: 0, y: 1 });
});
