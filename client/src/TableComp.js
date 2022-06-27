import './TableComp.css';

function TableComp({ matchesList }) {

    matchesList.sort((match1, match2) => match1.country_name.localeCompare(match2.country_name))

    return (
      <div className="wrapper">
          <span className="TableComp">
                <table>
                  <tbody>
                    <tr>
                        <th>Country</th>
                        <th>League</th>
                        <th>Match Name</th>
                        <th>Datetime</th>
                        <th>Status</th>
                        <th>Result</th>
                        <th>Winner</th>
                    </tr>
                </tbody>
                    {matchesList.map((val, i) => {
                                return (
                                    <tbody>

                                        <tr key={i}>
                                            <td>{val.country_name}</td>
                                            <td>{val.league_name}</td>
                                            <td>{val.name}</td>
                                            <td>{val.datetime}</td>
                                            <td>{val.status}</td>
                                            <td>{val.result}</td>
                                            <td>{val.winner}</td>
                                        </tr>
                                    </tbody>
                                )
                            })}
                </table>
          </span>
      </div>
    );
  }
export default TableComp;