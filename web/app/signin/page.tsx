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
        <Suspense fallback={null}>
          <PhoneSignIn />
        </Suspense>
      </section>
    </main>
  );
}
