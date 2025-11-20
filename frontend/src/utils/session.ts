import { v4 as uuidv4 } from 'uuid';

const SESSION_KEY = 'fhirside-session-id';

export function getOrCreateSessionId(): string {
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = uuidv4();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
}

export function createNewSession(): string {
  const sessionId = uuidv4();
  localStorage.setItem(SESSION_KEY, sessionId);
  return sessionId;
}

export function getSessionId(): string | null {
  return localStorage.getItem(SESSION_KEY);
}
