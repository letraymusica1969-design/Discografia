'use client';

import { useState } from 'react';

export default function Join() {
  const [sent, setSent] = useState(false);
  return (
    <section id="unete" className="section">
      <div className="unete">
        <p className="section-lbl">EL DESVÁN DEL VINILO</p>
        <h2>Unirte al club</h2>
        <p className="acerca" style={{ textAlign: 'center' }}>
          Primicias, material de archivo y la comunidad alrededor de Canciones de una Ciudad.
          Dejá tu email para recibir las novedades.
        </p>
        {sent ? (
          <p className="sent">¡Listo — bienvenido al club!</p>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setSent(true);
            }}
          >
            <input type="email" required placeholder="tu@email.com" />
            <button type="submit">Unirme</button>
          </form>
        )}
      </div>
    </section>
  );
}