import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import SearchPage from "./SearchPage"
import SearchByCompanyPage from "./SearchByCompanyPage";
import SearchByVacancy from "./SearchByVacancy";

function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <SearchPage />,
    },
    {
      path: "/searchByCompany",
      element: <SearchByCompanyPage />,
    },
    {
      path: "/searchByVacancy",
      element: <SearchByVacancy />,
    },
  ]);
  return (
      <RouterProvider router={router} />
  );
}

export default App;
