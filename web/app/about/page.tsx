import type { Metadata } from "next";
import { ListingForm } from "../listing-form";

export const metadata: Metadata = {
  title: "About Hidden Rent",
  description: "How Hidden Rent reads a listing and shows the energy bill it leaves out.",
};

const steps = [
  "01 / Paste a listing",
  "02 / See the real cost",
  "03 / Ask three questions",
  "04 / Cut cost and carbon. Compete.",
];

export default function AboutPage() {
  return (
    <main className="hero">
      <div className="hero-decor" aria-hidden="true">
        <img className="halo" src="/hero/halo.svg" alt="" />
        <img className="orbit" src="/hero/orbit.svg" alt="" />
        <img className="texture" src="/hero/texture.svg" alt="" />
      </div>
      <div className="hero-inner">
        <header className="edition">
          <p>A rental-energy transparency project</p>
          <p>Ann Arbor, MI / Field notes 001</p>
        </header>
        <section className="promise">
          <div className="entry">
            <h1 className="heading">
              The rent you
              <br />
              don&apos;t see.
            </h1>
            <p className="subhead">The listing tells half the story.</p>
            <p className="description">
              Hidden Rent shows the energy bill a rental listing doesn&apos;t, and the carbon behind it, then turns
              it into a score you can compare, improve and brag about.
            </p>
            <ListingForm />
          </div>
          <div className="collage">
            <img className="house" src="/hero/house.png" alt="Black and white photograph of a rental house" />
            <p className="annotation">LOOK PAST THE ASKING RENT.</p>
            <aside className="note">
              <p className="note-label eyebrow">
                <img src="/hero/zap.svg" alt="" width={16} height={16} />
                The bill behind the lease
              </p>
              <p className="amount">+$94 / MO</p>
              <p className="note-copy">Illustrative hidden-rent delta from PLAN. Not a property estimate.</p>
            </aside>
          </div>
        </section>
        <ol className="pathway">
          {steps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </div>
    </main>
  );
}
