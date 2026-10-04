import type { Metadata } from "next";
import { SignInButton } from "../sign-in-button";

export const metadata: Metadata = {
  title: "Sign in · Hidden Rent",
  description: "Sign in to save your Hidden Rent scores.",
};

export default function SignInPage() {
  return (
    <main className="survey-screen">
      <section className="dossier sign-in-card">
        <p className="eyebrow">Account</p>
        <h1 className="board-title">Sign in to save your scores</h1>
        <p className="board-note">
          Your score stays on this device until an account is connected. Sign-in uses the OAuth authorize redirect
          and returns here with a code. The token exchange waits on the provider.
        </p>
        <SignInButton className="action" />
      </section>
    </main>
  );
}
