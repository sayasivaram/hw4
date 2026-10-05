import "./About.css";

export default function About() {
  return (
    <div className="container about-page">
      <h1>About Campus Customs</h1>
      <p className="about-lede">
        Campus Customs started as a small operation serving Yale students, families, and alumni
        who wanted gear that actually reflected where they belonged on campus — their college,
        their team, their school.
      </p>

      <div className="about-grid">
        <div>
          <h3>Who We Serve</h3>
          <p>
            Current students outfitting their dorm room and their Saturdays, parents visiting for
            Family Weekend, alumni reliving their residential college days, and anyone cheering on
            the Bulldogs from the stands.
          </p>
        </div>
        <div>
          <h3>What We Carry</h3>
          <p>
            Hoodies, crewnecks, T-shirts, quarter-zips, and fleece jackets across every
            residential college, graduate school, and varsity team — officially licensed and
            built for everyday wear.
          </p>
        </div>
        <div>
          <h3>Where We Are</h3>
          <p>
            Rooted in New Haven, Connecticut, steps from Yale's campus, with an online storefront
            that ships Yale pride well beyond the Elm City.
          </p>
        </div>
      </div>
    </div>
  );
}
