





import sys,os
import winreg


def usage():
    #informs the user how to use the program correctly
    
    help_info = """ reg.py [Operation] [Parameter List] 
        Operation [ QUERY   :   ADD     : DELETE ]

        /v Value
        /t DataType
        /d Data
        /se Separator

        EXAMPLES:
            reg.py ADD <keyname> [ /v Value] [ /t DataType] [ /se Seperator] [ /d Data]
            reg.py DELETE <keyname>                (Deletes entire key file)
            reg.py DELETE <keyname> [/v Value]     (Deletes specific value from registry)
            reg.py QUERY <keyname>                 (Returns all values in key)
            reg.py QUERY  <keyname>  [/v Value]    (Returns the queried value)     
    """
    print(help_info)



def checkValidOperation(operation):
    #checks that the requested operation is valid 
    validOperations = ["ADD", "DELETE", "QUERY"]
    
    if (operation.upper() in validOperations):
        #return true if requested operation is valid
        return True
    
    #Program defaults to false 
    print("Invalid Operation '%s'" % operation)
    print("VALID OPERATIONS ARE ADD, QUERY DELETE")
    return False



def addRegistryKey(filename, arguments):

    #makes sure the number of arguments is even
    #eg each parameter should have one corresponding value
    if ((len(arguments) % 2) != 0 ):
        print("Number of arguments should be even, Please check your input")
        usage()
        sys.exit(1)
    
    #The following segments are used to store the input arguments
    #retrieves separator from arguments
    if ("/se" in arguments):  
        sep_pos = arguments.index["/s"] + 1
        separator = arguments[sep_pos]
    else:
        separator = ":"

    #retrieves value name from arguments
    if ("/v" in arguments):
        value_pos = arguments.index("/v") + 1
        value_Name = arguments[value_pos]
    else:
        value_Name = None

    #retrieves data type from arguments
    if ("/t" in arguments):
        type_pos = arguments.index("/t") + 1
        data_type = arguments[type_pos]
    else: 
        data_type = None

    #Retrieves data from arguments
    if ("/d" in arguments):
        data_pos = arguments.index("/d") + 1
        data_data = arguments[data_pos]
    else:
        data_data = "(value not set)"


#========================================================================
#========================================================================

    #converts data to integer, used in case input datatype is non-string
    """
    try:
        data_data = int(data_data)
    except:
        data_data = str(data_data)
    """

    #used to split filename into appropiate sections
    filename_list = filename.split("\\")

    hive_name = filename_list[0] 
    #input path name, minus hive name
    complete_path = filename_list[1:]
    #name of subkey
    subkey_name = filename_list[-1]


    #reconstructs the proper path
    main_path = ""
    for i in complete_path:
        main_path += i + "\\"  

    #creates new key, or opens key if key already exists
    key_object = createKeyObject(hive_name, main_path)
    #creates winreg object for the input data type
    winreg_type = returnDataTypeObject(data_type)
    
    #set values for new key
    winreg.SetValueEx(key_object, value_Name, 0, winreg_type, data_data)

    #close file after we are done
    key_object.Close()

    #exit cleanly
    return 0






def createKeyObject(hive_name, main_path):
    #Factory used to create new key objects for addRegistryKey

    #remove any whitespace and fix for upper or lower case arguments
    hive_name = hive_name.strip().upper()

    #returns the appropriate registry file object for the specified hive/path
    #note that "winreg.KEY_ALL_ACCESS" is probably a security no-no
    #but I was having issues when opening certain registry files and that seemed
    #to be the only way i could find to fix it. 

    #There are still issues when opening "important" reg files
    #I assume this is because they are locked by the system, or they are in use
    try:
        if hive_name == "HKEY_CURRENT_USER":
            return winreg.CreateKey(winreg.HKEY_CURRENT_USER, main_path)

        elif hive_name == "HKEY_LOCAL_MACHINE" or hive_name == "HKLM":
            return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, \
            main_path, 0, winreg.KEY_ALL_ACCESS)
        
        elif hive_name == "HKEY_USERS":
            return winreg.OpenKey(winreg.HKEY_USERS, \
            main_path, 0, winreg.KEY_ALL_ACCESS)

        elif hive_name == "HKEY_CLASSES_ROOT":
            return winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, \
            main_path, 0, winreg.KEY_ALL_ACCESS)

        elif hive_name == "HKEY_CURRENT_CONFIG" or hive_name == "HKCC":
            return winreg.CreateKey(winreg.HKEY_CURRENT_CONFIG, main_path)

    except:
        print("ERROR, UNABLE TO OPEN FILE, CHECK FILENAME AND ENSURE YOU HAVE \
                APPROPRIATE PERMISSIONS TO ACCESS THE SPECIFIED FILE")
        sys.exit(1)


    

def returnDataTypeObject(datatype):
    #factory pattern used for dynamically returning winreg type objects
    
    #set to default registry datatype in none given
    if datatype == None:
        return winreg.REG_SZ

    #fix case so that upper or lower case arguments can be used
    check_type = datatype.strip().upper()

    #compare to known types and return associated winreg type object
    if check_type == "REG_SZ":
        return winreg.REG_SZ
    elif check_type == "REG_BINARY":
        return winreg.REG_BINARY
    elif check_type == "REG_DWORD":
        return winreg.REG_DWORD
    elif check_type == "REG_LINK":
        return winreg.REG_DWORD
    #more to add later
    
    



def deleteRegistryKey(filename, arguments):
    #program used to delete registry key files
    #can delete specific values, or entire keys
  
    #get value that needs to be deleted
    if ("/v" in arguments):
        value_pos = arguments.index("/v") + 1
        value_to_delete = arguments[value_pos]
    else:
        value_to_delete = None


#=============================================================================
#=============================================================================


    #used to split filename into appropiate sections
    file_list = filename.split("\\")
    
    hive_name = file_list[0]
    #contains entire path, minus hive name
    complete_path = file_list[1:]
    #contains input path, minus hive name and final subkey
    key_path = file_list[1:-1]
    #contains name of final subkey
    subkey_name = file_list[-1]
    
    #index used to seperate hive name from the key name
    hive_index = filename.index("\\")
    #whole path, minus the main hive name
    path_inc_subkey = filename[hive_index+1:]
    
    
    #reconstructs the file path, minus subkey
    #this was needed to separate the subkey from the main key
    main_path = ""
    for i in key_path[:-1]:
        main_path += i + "\\"  
    main_path += key_path[-1]
  
    #main key object, used for deleting the entire subkey 
    mainkey_object = createKeyObject(hive_name, main_path)
    
    #subkey object, used for deleting specific values from a subkey
    subkey_object = createKeyObject(hive_name, path_inc_subkey)
    
   
    try:
        #tuple consists of (subkey count, value count, date since modified)
        #this is needed to determine if the whole key can be deleted
        #without any subkeys causing issues (needs to have 0 subkeys)
        num_subkeys, num_values, garbage = winreg.QueryInfoKey(subkey_object)
    except:
        print("error accessing file, is the file empty?")
        sys.exit(1)

    #delete all values in key, if key contains no subkeys
    # and if no specific value was specified
    if (value_to_delete == None):
        if (num_subkeys == 0):
            try:
                #deletes whole subkey
                winreg.DeleteKey(mainkey_object, subkey_name)
            except: 
                print("Can not delete key until all subkeys are removed")
                print("Requested registry key contains %i subkeys" % num_subkeys)
                sys.exit(1)

    

    #delete specific value if one is specified
    if (value_to_delete != None):
        try:
            winreg.DeleteValue(subkey_object, value_to_delete)
        except:
            print("Failed to delete value, are you sure the value exists??")
            sys.exit(1)
    


    #close key objects and exit function 
    mainkey_object.Close()
    subkey_object.Close()
    return 0





def queryRegistryKey(filename, arguments):
    #program for querying registry keys
    #returns subkeys if no value specified
    #returne value if a specific value is specified


    #exit program if not enough arguments 
    if (len(arguments) % 2 != 0):
        usage()
        sys.exit(1)

    #gets the query value from arguments
    if ("/v" in arguments):
        value_pos = arguments.index("/v") + 1
        value_to_query = arguments[value_pos]
    else:
        value_to_query = None

#=========================================================================
#=========================================================================

    #used to split filename into appropriate sections
    file_list = filename.split("\\")
    main_path = ""
    complete_path = ""
    hive_name = file_list[0] 
    #splits
    if (len(file_list) > 1):
        complete_path = file_list[1:]
    #assigns name of subkey, 
    subkey_name = file_list[-1]
    
    
    #reconstructs the proper path
    #edited to account for queries of root keys
    for i in complete_path[:-1]:
        main_path += i + "\\"  
    
    if (complete_path != ""):
        main_path += complete_path[-1]
    
    #create new key object for use with winreg methods
    key_object = createKeyObject(hive_name, main_path)
    
    
    #returns a tuple containing information about the key object
    #this is needed to print all values if no particular value is specified
    try:
        #note that garbage corresponds to a value that is of no use to us
        #in this case, it is a time since the key was last modified
        num_subkeys, num_values, garbage = winreg.QueryInfoKey(key_object)
    except:
        print("error accessing file, is the file empty?")
        sys.exit(1)


    #print all subkeys in the specified key, if no particular value was specified
    #if there are no subkeys, prints all values in the key
    if (value_to_query == None):
        #iterate through the key and print all subkeys, if there are any
        if (num_subkeys != 0):
            for i in range(0, num_subkeys):
                #prints the full name of the contained subkeys 
                print(hive_name + "\\" + main_path + "\\" + winreg.EnumKey(key_object, i))
        elif (num_subkeys == 0):
            for i in range(0, num_values):
                #retrieve name and data value from registry file
                #throw away final value as it is not needed
                name, data, trash = winreg.EnumValue(key_object, i)
                #set name to defaulti if it is blank, for nicer output
                if (name == ""):
                    name = "(Default)"
                print(name + ":" + data)
    else:
        #prints a specific value, if a specific value was specified in arguments
        try:
            #in this case, garbage corresponds to an integer relating to the
            #registry type, we don't need this. 
            data, garbage = winreg.QueryValueEx(key_object, value_to_query)
            print(value_to_query + ":" + data)
        except:
            print("Unable to find that value, please check your input and try again")
            sys.exit(1)

    #close registry object when done
    key_object.Close()

    return 0



def main():    

    # exits function if minimum number of arguments has not been met
    if (len(sys.argv) < 3):
        usage()
        sys.exit(1)

    # sets the requested operation and removes any whitespace
    # also sets the argument to upper case, so that lower or upper case can be used
    # in the arguments, eg add or ADD
    operation = sys.argv[1].strip().upper()
    

    # checks that the requested operation is valid (eg ADD, QUERY, DELETE)
    if (checkValidOperation(operation) == False):
        usage()
        sys.exit(1)


    # get registry location from main arguments
    registry_location = sys.argv[2]
    
    # used to make it easier to parse arguments of unknown lengths
    # the argparse module may possibly have been a better way of achieving this
    # but I had issues getting argparse to work with unknown/irregular argument numbers
    arguments = sys.argv[3:]
    
    # execute requested operation
    if (operation == "ADD"):
        addRegistryKey(registry_location, arguments)
    elif (operation == "DELETE"):
        deleteRegistryKey(registry_location, arguments)
    elif (operation == "QUERY"):
        queryRegistryKey(registry_location, arguments)
    else:
        #exit program if something went wrong
        sys.exit(1)

    # exit main cleanly if no errors occured
    return 0


# default entry point
if __name__=="__main__":
    main()

