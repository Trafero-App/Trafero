import {IoMdBus} from 'react-icons/io'

const ShowBussesButton = ({
    handleShowBussesClick, 
    isShowingBusses
}) => {
    return(
        <div 
        className={`mr-3 pointer-events-auto flex justify-center items-center h-14 min-w-14 lg:h-12 lg:min-w-12 rounded-xl bg-white shadow-md ${!isShowingBusses &&'opacity-90 hover:opacity-100 transition duration-200'}`}
        style={{cursor: 'pointer'}}
        onClick={handleShowBussesClick}
        >
            <IoMdBus className={`h-9 w-9 lg:h-7 lg:w-7 ${!isShowingBusses ? 'text-gray4' : 'text-blue2'} transition duration-200`}/>
        </div>
    )
}

export default ShowBussesButton