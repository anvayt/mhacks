"use client";

const STATE_KEY = "hiddenrent_oauth_state";

export function startScoreOAuth() {
  const state = crypto.randomUUID();
  sessionStorage.setItem(STATE_KEY, state);
  const redirectUri = `${window.location.origin}/auth/callback`;
  const authorize = process.env.NEXT_PUBLIC_OAUTH_AUTHORIZE_URL;
  const clientId = process.env.NEXT_PUBLIC_OAUTH_CLIENT_ID;
  if (authorize && clientId) {
    const url = new URL(authorize);
    url.searchParams.set("response_type", "code");
    url.searchParams.set("client_id", clientId);
    url.searchParams.set("redirect_uri", redirectUri);
    url.searchParams.set("scope", "openid");
    url.searchParams.set("state", state);
    window.location.assign(url.toString());
    return;
  }
  const params = new URLSearchParams({ state, error: "provider_unconfigured" });
  window.location.assign(`/auth/callback?${params.toString()}`);
}

export function SignInButton({ className = "ghost-action" }: { className?: string }) {
  return (
    <button className={className} type="button" onClick={startScoreOAuth}>
      Sign in to save your scores
    </button>
  );
}
