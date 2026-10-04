"use client";

import { useRouter } from "next/navigation";
import { ListingForm } from "../listing-form";

export default function AddressPage() {
  const router = useRouter();

  return (
    <main className="survey-screen dim-screen">
      <ListingForm backHref="/" onPicked={() => router.push("/survey")} submitLabel="Next" />
    </main>
  );
}
