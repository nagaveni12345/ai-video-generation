import React from 'react';
import Navbar from './Navbar';
import Hero from './Hero';
import Features from './Features';
import AvatarShowcase from './AvatarShowcase';
import CTASection from './CTASection';

const Home = ({ active, setActive }) => {
  return (
    <main>
      <Navbar active={active} setActive={setActive} />
      <Hero />
      <Features />
      <AvatarShowcase />
      <CTASection />
    </main>
  );
};

export default Home;
