import Link from "next/link";

export default function StartScreen() {
  return (
    <main className="start-screen">
      <Link className="start-photo" href="/loading?next=/address">
        <img src="/hero/house.png" alt="" />
        <span className="start-photo-label">Start</span>
      </Link>
    </main>
  );
}
