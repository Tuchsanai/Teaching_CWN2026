/**
 * PostgreSQL advisory lock used to pause the dispatcher during a test reset (DESIGN §7.2).
 * Reset: pg_advisory_lock(RESET_LOCK_KEY) … pg_advisory_unlock(RESET_LOCK_KEY).
 * Dispatcher loop: skip the round unless pg_try_advisory_lock_shared(RESET_LOCK_KEY) is true,
 * and release it with pg_advisory_unlock_shared(RESET_LOCK_KEY) at the end of the round.
 */
export const RESET_LOCK_KEY = 724_372_001;
