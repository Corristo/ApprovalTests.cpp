#ifndef APPROVALTESTS_CPP_DIFFINFO_H
#define APPROVALTESTS_CPP_DIFFINFO_H

#include <string>
#include "ApprovalTests/utilities/FileUtils.h"
#include "ApprovalTests/utilities/StringUtils.h"
#include "ApprovalTests/utilities/SystemUtils.h"

namespace ApprovalTests {
enum class Type { TEXT, IMAGE, TEXT_AND_IMAGE };



struct DiffInfo
{
    DiffInfo(std::string program, Type type) :
        program(program),
        arguments("%s %s"),
        type(type)
    {
    }
    DiffInfo(std::string program, std::string arguments, Type type) :
        program(program),
        arguments(arguments),
        type(type)
    {
    }
    std::string program;
    std::string arguments;
    Type type;

    std::string getProgramForOs() const
    {
        std::string result = program;
        if (result.rfind("{ProgramFiles}", 0) == 0)
        {
            const std::vector<const char*> envVars =
            {
                "ProgramFiles",
                "ProgramW6432",
                "ProgramFiles(x86)"
            };

            for(const auto& envVar : envVars)
            {
                std::string envVarValue = SystemUtils::safeGetEnv(envVar);
                if (envVarValue.empty())
                {
                    continue;
                }
                envVarValue += '\\';

                auto result1 = StringUtils::replaceAll(result, "{ProgramFiles}", envVarValue);
                if (FileUtils::fileExists(result1))
                {
                    return result1;
                }
            }
        }
        return result;
    }
};
}

#endif //APPROVALTESTS_CPP_DIFFINFO_H
