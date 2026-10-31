
def calculate_cost(interval, A, B):
    """
    Simplified backup cost model.
    interval: time between backups, in hours.
    A, B: illustrative model parameters.
    """
    return A / interval + B * interval


def gradient_descent(A, B, initial_interval=24.0,
                     learning_rate=1.0, max_iterations=1000):
    """
    Find a suitable backup interval using projected
    Gradient Descent with a backtracking line search.
    """
    if A <= 0 or B <= 0:
        raise ValueError("A and B must be positive.")

    min_interval = 1.0
    max_interval = 168.0  # 7 days, in hours

    interval = max(min_interval, min(max_interval, initial_interval))
    history = []

    for iteration in range(max_iterations):
        cost = calculate_cost(interval, A, B)
        gradient = -A / (interval ** 2) + B

        history.append({
            "iteration": iteration,
            "interval": interval,
            "cost": cost,
            "gradient": gradient
        })

        if abs(gradient) < 1e-8:
            break

        # Backtracking: accept a step only if cost decreases.
        step_size = learning_rate
        accepted = False

        for _ in range(60):
            candidate = interval - step_size * gradient
            candidate = max(min_interval, min(max_interval, candidate))
            candidate_cost = calculate_cost(candidate, A, B)

            if candidate_cost < cost:
                interval = candidate
                accepted = True
                break

            step_size *= 0.5

        if not accepted:
            break

    # Record the final result.
    history.append({
        "iteration": len(history),
        "interval": interval,
        "cost": calculate_cost(interval, A, B),
        "gradient": -A / (interval ** 2) + B
    })

    return interval, calculate_cost(interval, A, B), history


if __name__ == "__main__":
    # Illustrative values for testing only.
    A = 144.0
    B = 0.25

    best_interval, minimum_cost, history = gradient_descent(
        A, B, initial_interval=24.0
    )

    print("SMARTCLOUD ARCHIVE - OPTIMIZATION RESULTS")
    print("-----------------------------------------")
    print(f"Initial interval: 24 hours")
    print(f"Optimal backup interval: {best_interval:.2f} hours")
    print(f"Minimum model cost: {minimum_cost:.2f}")
    print(f"Iterations recorded: {len(history)}")
