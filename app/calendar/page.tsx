export default function Page() {
  return (
    <>
      <section className="intro">
        <p className="eyebrow">MAKE SPACE FOR LIFE</p>
        <h1>Calendar</h1>
        <p>A sample day with room to breathe. No calendar is connected.</p>
      </section>
      <section className="card">
        <p className="eyebrow">EXAMPLE AGENDA · NOT LIVE EVENTS</p>
        <h2>A slower kind of day</h2>
        <ol className="agenda">
          <li>
            <time>09:00</time>
            <div>
              <h3>A little focus time</h3>
              <p>One idea. A warm drink. No distractions.</p>
            </div>
          </li>
          <li>
            <time>12:30</time>
            <div>
              <h3>Step outside</h3>
              <p>Leave a little room for the unexpected.</p>
            </div>
          </li>
          <li>
            <time>17:00</time>
            <div>
              <h3>Close the loop</h3>
              <p>Notice what moved forward today.</p>
            </div>
          </li>
        </ol>
      </section>
    </>
  );
}
