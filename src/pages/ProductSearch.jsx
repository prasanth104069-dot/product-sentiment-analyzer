import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import BackgroundShader from '../components/BackgroundShader';
import Sidebar from '../components/Sidebar';

const ProductSearch = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [platform, setPlatform] = useState('Both');
  const [sortBy, setSortBy] = useState('Most Relevant');
  const [minRating, setMinRating] = useState(3.5);
  const [reviewsVolume, setReviewsVolume] = useState(5000);

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const q = searchParams.get('q');
    if (q !== null) {
      setQuery(q);
    }
  }, [searchParams]);

  useEffect(() => {
    if (query) {
      setLoading(true);
      fetch(`http://127.0.0.1:8000/api/products?search=${query}`)
        .then(res => res.json())
        .then(data => {
          setProducts(data.summary || []);
          setLoading(false);
        })
        .catch(err => {
          console.error(err);
          setLoading(false);
        });
    } else {
      setProducts([]);
    }
  }, [query]);

  const handleSearchClick = (e) => {
    e.preventDefault();
    setSearchParams({ q: query });
  };

  return (
    <div className="bg-background text-on-surface antialiased overflow-x-hidden min-h-screen relative">
      <BackgroundShader />
      <Sidebar isMobileOpen={isMobileOpen} setIsMobileOpen={setIsMobileOpen} />

      <main className="md:ml-64 p-margin-mobile md:p-margin-desktop min-h-screen">
        <div className="flex items-center gap-2 md:hidden mb-6 pt-16">
          <button 
            onClick={() => setIsMobileOpen(true)}
            className="w-10 h-10 rounded-xl glass-card flex items-center justify-center text-on-surface"
          >
            <span className="material-symbols-outlined">menu</span>
          </button>
          <span className="font-extrabold text-primary text-xl">SentientAI</span>
        </div>

        <section className="flex flex-col items-center justify-center text-center mb-12 mt-4">
          <h1 className="text-3xl md:text-5xl font-black mb-4 text-on-surface">Analyze Sentiment. Discover Truth.</h1>
          <p className="text-sm md:text-md text-on-surface-variant max-w-2xl mb-8">
            Advanced AI sentiment processing for Amazon and Flipkart products. Turn millions of customer reviews into actionable emotional insights.
          </p>

          <form onSubmit={handleSearchClick} className="w-full max-w-3xl glass-card rounded-2xl p-2 flex items-center shadow-lg bg-white/60">
            <div className="flex-grow flex items-center px-4">
              <span className="material-symbols-outlined text-primary text-2xl mr-3">psychology</span>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-transparent border-none focus:ring-0 text-sm text-on-surface placeholder:text-outline py-3 outline-none"
                placeholder="Search products by name or paste marketplace link..."
                type="text"
              />
            </div>
            <button
              type="submit"
              className="bg-primary text-white flex items-center gap-2 px-6 py-3 rounded-xl font-bold shadow-md shadow-primary/20 hover:scale-98 transition-all group"
            >
              <span>Search Analyzer</span>
              <span className="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform">arrow_forward</span>
            </button>
          </form>
        </section>

        <section className="mb-10">
          <div className="flex flex-wrap items-center justify-between gap-6 glass-card p-6 rounded-2xl bg-white/70">
            <div className="flex flex-wrap gap-6 items-center">
              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase font-bold text-outline">Platform</span>
                <div className="flex bg-surface-container rounded-lg p-1 text-xs">
                  {['Both', 'Amazon', 'Flipkart'].map((plat) => (
                    <button
                      key={plat}
                      onClick={() => setPlatform(plat)}
                      className={`px-3 py-1.5 rounded-md font-bold transition-all ${
                        platform === plat 
                          ? 'bg-white shadow-sm text-primary' 
                          : 'text-on-surface-variant hover:text-primary'
                      }`}
                    >
                      {plat}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase font-bold text-outline">Sort By</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-surface-container border-none rounded-lg text-xs font-semibold text-on-surface py-2 pl-3 pr-8 outline-none focus:ring-1 focus:ring-primary/20"
                >
                  <option>Most Relevant</option>
                  <option>Highest Sentiment</option>
                  <option>Popularity</option>
                  <option>Review Volume</option>
                </select>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase font-bold text-outline">Min Rating</span>
                <div className="flex items-center gap-2 text-xs">
                  <input
                    type="range"
                    min="1"
                    max="5"
                    step="0.5"
                    value={minRating}
                    onChange={(e) => setMinRating(parseFloat(e.target.value))}
                    className="accent-primary w-24 cursor-pointer"
                  />
                  <span className="font-bold text-on-surface">{minRating} ★+</span>
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] uppercase font-bold text-outline font-semibold">Min Reviews</span>
                <div className="flex items-center gap-2 text-xs">
                  <input
                    type="range"
                    min="100"
                    max="10000"
                    step="500"
                    value={reviewsVolume}
                    onChange={(e) => setReviewsVolume(parseInt(e.target.value))}
                    className="accent-primary w-24 cursor-pointer"
                  />
                  <span className="font-bold text-on-surface">{(reviewsVolume / 1000).toFixed(1)}k+</span>
                </div>
              </div>
            </div>

            <button className="flex items-center gap-2 text-primary font-bold text-xs hover:bg-primary/5 px-4 py-2 rounded-lg transition-all">
              <span className="material-symbols-outlined text-sm">tune</span>
              <span>Advanced Filters</span>
            </button>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">

          {loading && (
            <div className="col-span-full py-16 flex flex-col items-center justify-center text-center">
              <span className="material-symbols-outlined text-5xl text-primary mb-4 animate-spin">refresh</span>
              <h3 className="text-xl font-bold text-on-surface">Searching...</h3>
            </div>
          )}

          {!loading && products.length > 0 ? (
            products.map((p) => (
  <div
    key={p.id}
    className="glass-card rounded-3xl overflow-hidden hover:translate-y-[-4px] hover:shadow-xl transition-all duration-300 flex flex-col group bg-white/70"
  >
    <div className="w-full h-40 bg-surface-container overflow-hidden flex items-center justify-center">
      {p.image_url && p.image_url !== "N/A" ? (
        <img
          src={p.image_url}
          alt={p.title || p.name}
          className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
          onError={(e) => { e.target.style.display = 'none'; }}
        />
      ) : (
        <span className="material-symbols-outlined text-5xl text-outline">image_not_supported</span>
      )}
    </div>

    <div className="p-6 flex flex-col flex-grow">
      <div className="flex justify-between items-start mb-3">
        <span className={`text-white px-3 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider shadow-lg ${
          p.badgeType === 'negative' ? 'bg-error' : p.badgeType === 'trending' ? 'bg-secondary' : 'bg-primary'
        }`}>
          {p.badge}
        </span>
        <span className="font-bold text-[9px] uppercase tracking-wider text-secondary bg-secondary/10 px-2 py-0.5 rounded-full">
          {p.source}
        </span>
      </div>

      <h3 className="font-bold text-lg text-on-surface leading-snug mb-2 group-hover:text-primary transition-colors line-clamp-2">
        {p.title || p.name}
      </h3>

      {p.specs && Object.keys(p.specs).length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {Object.entries(p.specs).slice(0, 3).map(([key, value]) => (
            <span key={key} className="text-[10px] bg-surface-container px-2 py-1 rounded-md text-on-surface-variant">
              {key}: {value}
            </span>
          ))}
        </div>
      )}

      <div className="flex justify-between items-center mt-auto pt-4 border-t border-white/20">
        <div>
          <span className="text-[10px] text-outline font-semibold">Rating</span>
          <p className="font-bold text-on-surface text-sm">{p.rating}</p>
        </div>
        <div>
          <span className="text-[10px] text-outline font-semibold">Reviews</span>
          <p className="font-bold text-on-surface text-sm">{p.reviews}</p>
        </div>
        <div>
          <span className="text-[10px] text-outline font-semibold">Positive</span>
          <p className="font-bold text-primary text-sm">{p.positive}%</p>
        </div>
      </div>
    </div>
  </div>
))
          

  ) : !loading && query ? (
      <div className="col-span-full py-16 flex flex-col items-center justify-center text-center">
       <span className="material-symbols-outlined text-5xl text-outline mb-4">search_off</span>
        <h3 className="text-xl font-bold text-on-surface mb-2">No Products Found</h3>
        <p className="text-sm text-on-surface-variant max-w-md">
                We couldn't find any products matching "{query}". Try adjusting your filters or search keywords.
              </p>
            </div>
          ) : null}

        </section>
      </main>
    </div>
  );
};

export default ProductSearch;