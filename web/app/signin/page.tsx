import type { Metadata } from "next";
import { Suspense } from "react";
import { PhoneSignIn } from "../sign-in-button";

export const metadata: Metadata = {
  title: "Sign in · Hidden Rent",
  description: "Sign in with your phone number to save your Hidden Rent scores.",
};

export default function SignInPage() {
  return (
    <main className="survey-screen dim-screen">
      <section className="dossier sign-in-card">
        <p className="eyebrow">Account</p>
        <h1 className="board-title">Sign in to save your scores</h1>
        <Suspense fallback={null}>
          <PhoneSignIn />
        </Suspense>
      </section>
    </main>
  );
}
