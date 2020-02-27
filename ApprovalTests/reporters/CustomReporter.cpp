#include "CustomReporter.h"

#include "DiffInfo.h"

namespace ApprovalTests
{
    std::shared_ptr<GenericDiffReporter>
    CustomReporter::create(std::string path, Type type)
    {
        return create(std::move(path), DiffInfo::getDefaultArguments(), type);
    }

    std::shared_ptr<GenericDiffReporter>
    CustomReporter::create(std::string path, std::string arguments, Type type)
    {
        DiffInfo info(std::move(path), std::move(arguments), type);
        return std::make_shared<GenericDiffReporter>(info);
    }

    std::shared_ptr<GenericDiffReporter>
    CustomReporter::createForegroundReporter(std::string path, Type type)
    {
        return createForegroundReporter(
            std::move(path), DiffInfo::getDefaultArguments(), type);
    }

    std::shared_ptr<GenericDiffReporter>
    CustomReporter::createForegroundReporter(std::string path,
                                             std::string arguments,
                                             Type type)
    {
        DiffInfo info(std::move(path), std::move(arguments), type);
        auto reporter = std::make_shared<GenericDiffReporter>(info);
        reporter->launcher.setForeground(true);
        return reporter;
    }
}
