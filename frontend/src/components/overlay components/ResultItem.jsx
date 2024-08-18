const ResultItem = ({
    data,
    handleResultItemClick
}) => {

    return(
        <div 
        className='pointer-events-auto px-5 flex items-center text-sm h-12 hover:bg-gray1 transition duration-200'
        onClick={() => handleResultItemClick(data)}
        style={{cursor: 'pointer'}}
        >
            {data.properties.type=='city' ?
            <>
                <h1 className='font-semibold'>{`${data.properties.name}`}</h1>{`, ${data.properties.county!=null ? data.properties.county : data.properties.state}`}
            </>
            : data.properties.type=="house" ?
            <>
                <h1 className='font-semibold'>{`${data.properties.name}`}</h1>{`, ${data.properties.locality!=null ? data.properties.locality : data.properties.city}`}
            </>  
            : data.properties.type=='street' ?
            <>
                <h1 className='font-semibold'>{`${data.properties.name}`}</h1>{`, ${data.properties.city}`}
            </> 
            : data.properties.type=='district' ?
            <>
                <h1 className='font-semibold'>{`${data.properties.name}`}</h1>{`, ${data.properties.state}`}
            </> 
            : data.properties.type=='state' ?
            <>
                <h1 className='font-semibold'>{`${data.properties.name}`}</h1>{`, ${data.properties.country}`}
            </> 
            : data.properties.type=='county' ?
            <>
                <h1 className='font-semibold'>{`${data.properties.name}`}</h1>{`, ${data.properties.state}`}
            </> 
            : data.properties.type=='coordinate' ?
            <>
                <h1 className='font-semibold'>{data.properties.name}</h1>
            </> 
            : <h1>{data.properties.type}</h1>
            }
        </div>
    )
}

export default ResultItem