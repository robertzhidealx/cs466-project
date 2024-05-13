import { Inter } from "next/font/google";
import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export default function Home() {
  const params = useSearchParams();
  const router = useRouter();

  const [loading, setLoading] = useState(false);

  const [title, setTitle] = useState("");
  const [query, setQuery] = useState("");
  const [author, setAuthor] = useState("");
  const [stem, setStem] = useState(true);
  const [removestop, setRemovestop] = useState(true);
  const [weighting, setWeighting] = useState("tfidf");
  const [similarity, setSimilarity] = useState("cosine");
  const [weights, setWeights] = useState("114");
  const [domain, setDomain] = useState("hub.jhu.edu");
  const [customDomain, setCustomDomain] = useState("");
  const [online, setOnline] = useState(false);
  const [numPages, setNumPages] = useState(100);

  const [numDocs, setNumDocs] = useState(5);

  const [docs, setDocs] = useState([]);

  const handleSearch = (
    title,
    query,
    author,
    stem,
    removestop,
    weighting,
    similarity,
    weights,
    numDocs,
    domain,
    online,
    numPages,
    customDomain
  ) => {
    setLoading(true);
    fetch(
      `http://127.0.0.1:5000/search?title=${title}&query=${query}&author=${author}&stem=${stem}&remove=${removestop}&weighting=${weighting}&similarity=${similarity}&weights=${weights}&count=${numDocs}&domain=${
        domain === "custom" ? customDomain : domain
      }&online=${online}&numPages=${numPages}`
    )
      .then((response) => {
        setLoading(false);
        return response.json();
      })
      .then(setDocs)
      .catch((error) => {
        setLoading(false);
        console.error(error);
      });
  };

  const scrolltoHash = (id) => {
    const element = document.getElementById(id);
    element?.scrollIntoView({
      behavior: "smooth",
      inline: "nearest",
    });
  };

  useEffect(() => {
    if (params.size) {
      const title = params.get("title") || "";
      const query = params.get("query") || "";
      const author = params.get("author") || "";
      const stem = params.get("stem") ? params.get("stem") === "true" : true;
      const removestop = params.get("remove")
        ? params.get("remove") === "true"
        : true;
      const weighting = params.get("weighting") || "tfidf";
      const similarity = params.get("similarity") || "cosine";
      const weights = params.get("weights") || "1341";
      const numDocs = params.get("count") || "5";
      const domain = params.get("domain") || "hub.jhu.edu";

      if (title) setTitle(title);
      if (query) setQuery(query);
      if (author) setAuthor(author);
      if (stem) setStem(stem);
      if (removestop) setRemovestop(removestop);
      if (weighting) setWeighting(weighting);
      if (similarity) setSimilarity(similarity);
      if (weights) setWeights(weights);
      if (numDocs) setNumDocs(numDocs);
      if (domain) setDomain(domain);

      handleSearch(
        title,
        query,
        author,
        stem,
        removestop,
        weighting,
        similarity,
        weights,
        numDocs,
        domain
      );
    }
  }, [params]);

  useEffect(() => {
    scrolltoHash(window.location.hash.slice(1));
  }, [docs]);

  return (
    <main className={`flex justify-center min-h-screen ${inter.className}`}>
      <div className="bg-white w-[1000px]">
        <h1
          className="py-4 text-lg text-center border-b hover:cursor-pointer"
          onClick={() => router.push("/")}
        >
          Hopkins Search Engine
        </h1>
        <div className="flex items-center justify-center h-12 mt-1">
          <input
            type="text"
            placeholder="Enter the title here"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="p-1 mr-2 text-center border rounded"
          />
          <input
            type="text"
            placeholder="Enter your query here"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="p-1 mr-2 text-center border rounded"
          />
          <input
            type="text"
            placeholder="Enter the author here"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            className="p-1 mr-2 text-center border rounded"
          />
        </div>
        <div className="flex items-center justify-center h-8 pb-2">
          <input
            type="checkbox"
            name="stem"
            checked={stem}
            onChange={(e) => setStem(e.target.checked)}
            className="mr-1"
          />
          <label className="mr-2">Stem?</label>
          <input
            type="checkbox"
            name="remove"
            checked={removestop}
            onChange={(e) => setRemovestop(e.target.checked)}
            className="mr-1"
          />
          <label className="mr-2">Remove stopwords?</label>
          <select
            name="weighting"
            value={weighting}
            onChange={(e) => setWeighting(e.target.value)}
            className="mr-2 text-sm text-center border rounded"
          >
            <option value="tf">Raw TF</option>
            <option value="tfidf">TF-IDF</option>
            <option value="boolean">Boolean</option>
          </select>
          <select
            name="similarity"
            value={similarity}
            onChange={(e) => setSimilarity(e.target.value)}
            className="mr-2 text-sm text-center border rounded"
          >
            <option value="cosine">Cosine</option>
            <option value="jaccard">Jaccard</option>
            <option value="dice">Dice</option>
            <option value="overlap">Overlap</option>
          </select>
          <select
            name="weights"
            value={weights}
            onChange={(e) => setWeights(e.target.value)}
            className="mr-2 text-sm text-center border rounded"
          >
            <option value="131">1,3,1</option>
            <option value="114">1,1,4</option>
            <option value="111">1,1,1</option>
          </select>
          <input
            type="text"
            placeholder="Number of docs"
            value={numDocs}
            onChange={(e) => setNumDocs(e.target.value)}
            className="mr-2 text-sm text-center border rounded w-36"
          />
        </div>
        <div className="flex items-center justify-center pb-2 border-b border-dashed">
          <label className="mr-1">Crawl from</label>
          <select
            name="domain"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            className="p-1.5 mr-2 text-sm text-center border rounded"
          >
            <option value="hub.jhu.edu">JHU Hub</option>
            <option value="jhunewsletter.com">JHU Newsletter</option>
            <option value="custom">Custom</option>
          </select>
          {domain === "custom" ? (
            <input
              type="text"
              onChange={(e) => setCustomDomain(e.target.value)}
              className="w-24 p-1.5 mr-2 text-sm text-center border rounded"
            />
          ) : null}
          <input
            type="checkbox"
            name="online"
            checked={online}
            onChange={(e) => setOnline(e.target.checked)}
            className="mr-1"
          />
          <label className="mr-1">Crawl latest?</label>
          <label className="mr-1">Crawl</label>
          <select
            name="numPages"
            value={numPages}
            onChange={(e) => setNumPages(e.target.value)}
            className="p-1.5 mr-1 text-sm text-center border rounded"
          >
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
            <option value={150}>150</option>
            <option value={200}>200</option>
            <option value={250}>250</option>
            <option value={300}>300</option>
            <option value={350}>350</option>
            <option value={400}>400</option>
            <option value={450}>450</option>
            <option value={500}>500</option>
          </select>
          <label className="mr-2">pages</label>
          {loading ? (
            <button
              disabled
              className="px-2 py-1 mr-2 text-center text-white bg-blue-400 border rounded"
            >
              Loading...
            </button>
          ) : (
            <button
              onClick={() =>
                handleSearch(
                  title,
                  query,
                  author,
                  stem,
                  removestop,
                  weighting,
                  similarity,
                  weights,
                  numDocs,
                  domain,
                  online,
                  numPages,
                  customDomain
                )
              }
              className="px-2 py-1 mr-2 text-center text-white transition bg-blue-500 border rounded hover:bg-blue-700 "
            >
              {(online ? "Crawl & " : "") + "Search"}
            </button>
          )}
        </div>
        <div className="mt-1">
          {docs.map((doc) => (
            <div key={doc.id} id={doc.id} className="px-4 py-2">
              <div className="flex items-center">
                <div className="flex items-center justify-center flex-none w-12 h-12 mr-2 text-white bg-blue-400 rounded">
                  <Link
                    href={`#${doc.id}`}
                    onClick={() => {
                      navigator.clipboard.writeText(
                        `http://localhost:3000/?query=${query}&author=${author}&stem=${stem}&remove=${removestop}&weighting=${weighting}&similarity=${similarity}&weights=${weights}#${doc.id}`
                      );
                    }}
                    className="transition hover:underline"
                  >
                    {doc.id}
                  </Link>
                </div>
                <div>
                  <a href={doc.url} className="text-blue-700 hover:underline">
                    {doc.title}
                  </a>
                  <div className="text-[14px]">{doc.author}</div>
                </div>
              </div>
              <p className="mt-2 text-sm">{doc.body + "..."}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
