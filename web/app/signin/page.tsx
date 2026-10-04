import type { Metadata } from "next";
import { Suspense } from "react";
import { PhoneSignIn } from "../sign-in-button";

export const metadata: Metadata = {
  title: "Sign in or sign up · Hidden Rent",
  description: "Use your phone number to save your home, commitments and progress on Hidden Rent.",
};

export default function SignInPage() {
  return (
    <main className="survey-screen dim-screen">
      <section className="dossier sign-in-card">
        <p className="eyebrow">Sign in or sign up</p>
        <h1 className="board-title">Save your home and progress</h1>
        <ul className="board-note" style={{ margin: 0, paddingLeft: 20, lineHeight: 1.8 }}>
          <li>Keep your grade and answers when you come back</li>
          <li>Save commitments and track your habit streak</li>
          <li>Optional monthly check-ins by text: you choose on the next step</li>
        </ul>
        <Suspense fallback={null}>
          <PhoneSignIn />
        </Suspense>
      </section>
    </main>
  );
}
