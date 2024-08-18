import {IoMdLocate} from 'react-icons/io'

const LocateButton = ({
    handleLocateClick, 
    isSharingLiveLocation
}) => {
    return(
        <div 
        className={`pointer-events-auto flex justify-center items-center h-14 min-w-14 lg:h-12 lg:min-w-12 rounded-xl bg-white shadow-md ${!isSharingLiveLocation &&'opacity-90 hover:opacity-100 transition duration-200'}`}
        style={{cursor: 'pointer'}}
        onClick={handleLocateClick}
        >
            <IoMdLocate className={`h-9 w-9 lg:h-7 lg:w-7 ${!isSharingLiveLocation ? 'text-gray4' : 'text-blue2'} transition duration-200`}/>
        </div>
    )
}

export default LocateButton